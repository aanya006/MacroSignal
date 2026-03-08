from datetime import datetime, timezone
from flask import Blueprint, jsonify

ingestion_bp = Blueprint('ingestion', __name__)


@ingestion_bp.route('/api/ingest', methods=['POST'])
def trigger_ingestion():
    """Manual trigger for news ingestion (dev/testing only)."""
    try:
        from app.services.news_ingestion import run_ingestion
        result = run_ingestion()
        return jsonify({
            "data": result,
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            "error": True,
            "message": str(e),
            "code": "INGESTION_ERROR"
        }), 500
