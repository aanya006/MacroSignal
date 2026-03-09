import json
import logging
import re
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.models.db import execute_query

logger = logging.getLogger(__name__)

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

memory_bp = Blueprint('memory', __name__)


@memory_bp.route('/api/memory/search')
def search_memory():
    """Search historical themes by keyword across theme names, descriptions, and article titles."""
    try:
        query = request.args.get("q", "").strip()

        if not query:
            return jsonify({
                "data": [],
                "meta": {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "count": 0,
                    "query": "",
                }
            })

        from_date = request.args.get("from", "").strip() or None
        to_date = request.args.get("to", "").strip() or None

        # Validate date format (YYYY-MM-DD)
        if from_date and not DATE_RE.match(from_date):
            from_date = None
        if to_date and not DATE_RE.match(to_date):
            to_date = None

        # Escape ILIKE wildcards in user input
        escaped = query.replace("%", "\\%").replace("_", "\\_")
        search_pattern = f"%{escaped}%"

        # Build optional date filter clauses
        date_clauses = ""
        date_params = []
        if from_date:
            date_clauses += " AND t.first_seen_at >= %s"
            date_params.append(from_date)
        if to_date:
            date_clauses += " AND t.last_updated_at <= %s"
            date_params.append(to_date)

        # Search themes where name/description match OR any linked article title matches
        # Rank by: direct theme match first, then by article count (proxy for relevance), then recency
        results = execute_query(
            f"""
            SELECT DISTINCT
                t.id, t.name, t.slug, t.description,
                t.score_label, t.score_value, t.article_count,
                t.first_seen_at, t.last_updated_at, t.causal_chain,
                CASE
                    WHEN t.name ILIKE %s THEN 3
                    WHEN t.description ILIKE %s THEN 2
                    ELSE 1
                END as relevance
            FROM themes t
            LEFT JOIN articles a ON a.theme_id = t.id
            WHERE t.first_seen_at < NOW() - INTERVAL '7 days'
               AND (t.name ILIKE %s
               OR t.description ILIKE %s
               OR a.title ILIKE %s){date_clauses}
            ORDER BY relevance DESC, t.last_updated_at DESC
            LIMIT 20
            """,
            (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, *date_params),
        )

        # Deduplicate (LEFT JOIN can produce dupes)
        seen_ids = set()
        unique_ids = []
        for r in results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                unique_ids.append(r["id"])

        if not unique_ids:
            return jsonify({
                "data": [],
                "meta": {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "count": 0,
                    "query": query,
                }
            })

        # Batch-fetch date ranges and peak temperatures (fixes N+1)
        id_tuple = tuple(unique_ids)
        placeholders = ",".join(["%s"] * len(id_tuple))

        date_ranges = execute_query(
            f"""
            SELECT theme_id, MIN(published_at) as earliest, MAX(published_at) as latest
            FROM articles
            WHERE theme_id IN ({placeholders}) AND published_at IS NOT NULL
            GROUP BY theme_id
            """,
            id_tuple,
        )
        date_map = {d["theme_id"]: d for d in date_ranges}

        peaks = execute_query(
            f"""
            SELECT DISTINCT ON (theme_id) theme_id, score_label, score_value
            FROM theme_history
            WHERE theme_id IN ({placeholders})
            ORDER BY theme_id, score_value DESC
            """,
            id_tuple,
        )
        peak_map = {p["theme_id"]: p for p in peaks}

        # Build enriched results preserving relevance order
        result_map = {}
        for r in results:
            if r["id"] not in result_map:
                result_map[r["id"]] = r

        enriched = []
        for tid in unique_ids:
            r = result_map[tid]
            dr = date_map.get(tid)
            date_range = {"earliest": None, "latest": None}
            if dr and dr["earliest"]:
                date_range = {
                    "earliest": dr["earliest"].isoformat() if hasattr(dr["earliest"], "isoformat") else dr["earliest"],
                    "latest": dr["latest"].isoformat() if hasattr(dr["latest"], "isoformat") else dr["latest"],
                }

            peak = peak_map.get(tid)
            peak_temperature = r["score_label"]
            if peak and peak["score_value"] and (peak["score_value"] > (r["score_value"] or 0)):
                peak_temperature = peak["score_label"]

            enriched.append({
                "id": r["id"],
                "name": r["name"],
                "slug": r["slug"],
                "description": r["description"],
                "score_label": r["score_label"],
                "article_count": r["article_count"],
                "date_range": date_range,
                "peak_temperature": peak_temperature,
                "causal_chain": json.loads(r["causal_chain"]) if isinstance(r.get("causal_chain"), str) else r.get("causal_chain"),
                "first_seen_at": r["first_seen_at"].isoformat() if hasattr(r.get("first_seen_at"), "isoformat") else r.get("first_seen_at"),
                "last_updated_at": r["last_updated_at"].isoformat() if hasattr(r.get("last_updated_at"), "isoformat") else r.get("last_updated_at"),
            })

        return jsonify({
            "data": enriched,
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "count": len(enriched),
                "query": query,
            }
        })

    except Exception as e:
        logger.exception("Memory search error: %s", e)
        return jsonify({
            "error": True,
            "message": "An internal error occurred while searching.",
            "code": "INTERNAL_ERROR"
        }), 500
