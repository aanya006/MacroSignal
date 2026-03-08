from datetime import datetime, timezone
from flask import Blueprint, jsonify

status_bp = Blueprint('status', __name__)


@status_bp.route('/api/status')
def get_status():
    try:
        from app.models.db import execute_query
        result = execute_query(
            "SELECT COUNT(*) as article_count FROM articles", fetch=True
        )
        article_count = result[0]['article_count'] if result else 0

        theme_result = execute_query(
            "SELECT COUNT(*) as theme_count FROM themes", fetch=True
        )
        theme_count = theme_result[0]['theme_count'] if theme_result else 0

        log_result = execute_query(
            "SELECT run_at FROM ingestion_logs ORDER BY run_at DESC LIMIT 1", fetch=True
        )
        last_ingestion = log_result[0]['run_at'].isoformat() + 'Z' if log_result else None

        return jsonify({
            "data": {
                "status": "ok",
                "article_count": article_count,
                "theme_count": theme_count,
                "last_ingestion": last_ingestion,
            },
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception:
        return jsonify({
            "data": {
                "status": "ok",
                "article_count": 0,
                "theme_count": 0,
                "last_ingestion": None,
            },
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        })
