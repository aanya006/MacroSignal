from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

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


@ingestion_bp.route('/api/ingest/backfill-images', methods=['POST'])
def backfill_images():
    """Scrape og:image for existing articles that have no image. Accepts ?batch=N (default 100)."""
    try:
        from app.services.news_ingestion import backfill_og_images
        batch = int(request.args.get("batch", 100))
        result = backfill_og_images(batch_size=batch)
        return jsonify({"data": result, "meta": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    except Exception as e:
        return jsonify({"error": True, "message": str(e), "code": "BACKFILL_ERROR"}), 500
