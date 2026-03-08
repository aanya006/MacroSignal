from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

from app.utils.cache import cache_get, cache_set
from app.models.db import execute_query

themes_bp = Blueprint('themes', __name__)


@themes_bp.route('/api/themes')
def get_themes():
    """List all themes ranked by temperature score."""
    try:
        # Try cache first
        cached = cache_get('macro:themes:all')
        if cached:
            return jsonify({
                "data": cached,
                "meta": {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "source": "cache",
                    "count": len(cached),
                }
            })

        # Fallback to database
        themes = execute_query(
            """
            SELECT id, name, slug, description, score_label, score_value, article_count,
                   region_tags, asset_tags, first_seen_at, last_updated_at
            FROM themes
            WHERE article_count > 0
            ORDER BY score_value DESC
            """
        )

        # Serialize datetimes
        for t in themes:
            if t.get("first_seen_at"):
                t["first_seen_at"] = t["first_seen_at"].isoformat()
            if t.get("last_updated_at"):
                t["last_updated_at"] = t["last_updated_at"].isoformat()

        return jsonify({
            "data": themes,
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "source": "database",
                "count": len(themes),
            }
        })

    except Exception as e:
        return jsonify({
            "error": True,
            "message": str(e),
            "code": "INTERNAL_ERROR"
        }), 500


def _serialize_datetime(obj):
    """Convert datetime fields to ISO strings."""
    for key in ("first_seen_at", "last_updated_at", "published_at", "ingested_at",
                "causal_chain_generated_at", "snapshot_date"):
        if obj.get(key) and hasattr(obj[key], "isoformat"):
            obj[key] = obj[key].isoformat()
    return obj


@themes_bp.route('/api/themes/<slug>')
def get_theme_detail(slug):
    """Get full theme detail by slug."""
    try:
        # Try cache first
        cache_key = f"macro:theme:{slug}"
        cached = cache_get(cache_key)
        if cached:
            return jsonify({
                "data": cached,
                "meta": {
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "source": "cache",
                }
            })

        # Fetch theme from DB
        themes = execute_query(
            """
            SELECT id, name, slug, description, score_label, score_value, article_count,
                   region_tags, asset_tags, causal_chain, causal_chain_generated_at,
                   first_seen_at, last_updated_at
            FROM themes WHERE slug = %s
            """,
            (slug,),
        )

        if not themes:
            return jsonify({
                "error": True,
                "message": f"Theme '{slug}' not found",
                "code": "NOT_FOUND"
            }), 404

        theme = _serialize_datetime(themes[0])

        # Get date range for timeline
        date_range = execute_query(
            """
            SELECT
                MIN(published_at) as earliest,
                MAX(published_at) as latest,
                array_agg(DISTINCT published_at::date ORDER BY published_at::date DESC) as article_dates
            FROM articles
            WHERE theme_id = %s AND published_at IS NOT NULL
            """,
            (theme["id"],),
        )

        if date_range and date_range[0]["earliest"]:
            dr = date_range[0]
            theme["date_range"] = {
                "earliest": dr["earliest"].isoformat() if hasattr(dr["earliest"], "isoformat") else dr["earliest"],
                "latest": dr["latest"].isoformat() if hasattr(dr["latest"], "isoformat") else dr["latest"],
            }
            theme["article_dates"] = [
                d.isoformat() if hasattr(d, "isoformat") else str(d)
                for d in (dr["article_dates"] or [])
            ]
        else:
            theme["date_range"] = {"earliest": None, "latest": None}
            theme["article_dates"] = []

        # Cache for 5 minutes
        cache_set(cache_key, theme, ttl=300)

        return jsonify({
            "data": theme,
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "source": "database",
            }
        })

    except Exception as e:
        return jsonify({
            "error": True,
            "message": str(e),
            "code": "INTERNAL_ERROR"
        }), 500


@themes_bp.route('/api/themes/<slug>/articles')
def get_theme_articles(slug):
    """Get articles for a theme, optionally filtered by date."""
    try:
        # Get theme ID
        themes = execute_query(
            "SELECT id FROM themes WHERE slug = %s", (slug,)
        )
        if not themes:
            return jsonify({
                "error": True,
                "message": f"Theme '{slug}' not found",
                "code": "NOT_FOUND"
            }), 404

        theme_id = themes[0]["id"]
        date_filter = request.args.get("date")

        if date_filter:
            articles = execute_query(
                """
                SELECT id, title, source_name, url, published_at, ai_summary,
                       region_tags, asset_tags
                FROM articles
                WHERE theme_id = %s AND published_at::date = %s
                ORDER BY published_at DESC
                """,
                (theme_id, date_filter),
            )
        else:
            articles = execute_query(
                """
                SELECT id, title, source_name, url, published_at, ai_summary,
                       region_tags, asset_tags
                FROM articles
                WHERE theme_id = %s
                ORDER BY published_at DESC
                """,
                (theme_id,),
            )

        # Serialize datetimes
        for a in articles:
            _serialize_datetime(a)

        return jsonify({
            "data": articles,
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "count": len(articles),
            }
        })

    except Exception as e:
        return jsonify({
            "error": True,
            "message": str(e),
            "code": "INTERNAL_ERROR"
        }), 500
