from datetime import datetime, timezone
from flask import Blueprint, jsonify

from app.utils.cache import cache_get
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
