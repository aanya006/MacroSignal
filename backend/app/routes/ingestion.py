from datetime import datetime, timezone
from flask import Blueprint, jsonify, request

ingestion_bp = Blueprint('ingestion', __name__)


@ingestion_bp.route('/api/ingest', methods=['POST'])
def trigger_ingestion():
    """Manual trigger for news ingestion (dev/testing only)."""
    from app.utils.config import INGESTION_ENABLED
    if not INGESTION_ENABLED:
        return jsonify({"error": True, "message": "Ingestion is disabled. Set INGESTION_ENABLED=true to enable.", "code": "INGESTION_DISABLED"}), 403
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


@ingestion_bp.route('/api/ingest/backfill-tags', methods=['POST'])
def backfill_tags():
    """Re-run classify_tags on all existing articles. Accepts ?batch=N (default 1000)."""
    try:
        from app.services.news_ingestion import backfill_tags as _backfill_tags
        batch = int(request.args.get("batch", 1000))
        result = _backfill_tags(batch_size=batch)
        return jsonify({"data": result, "meta": {"last_updated": datetime.now(timezone.utc).isoformat()}})
    except Exception as e:
        return jsonify({"error": True, "message": str(e), "code": "BACKFILL_ERROR"}), 500


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


@ingestion_bp.route('/api/admin/reclassify/<slug>', methods=['POST'])
def trigger_reclassify_theme(slug):
    """Reclassify only articles under a specific theme.

    Usage: POST /api/admin/reclassify/mas-sgd-policy
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Admin targeted reclassification triggered for '{slug}'")
    try:
        from app.services.theme_clustering import reclassify_theme
        result = reclassify_theme(slug)
        return jsonify({
            "data": result,
            "meta": {"last_updated": datetime.now(timezone.utc).isoformat()}
        })
    except ValueError as e:
        return jsonify({"error": True, "message": str(e), "code": "THEME_NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Targeted reclassification failed: {e}")
        return jsonify({"error": True, "message": str(e), "code": "RECLASSIFY_ERROR"}), 500


@ingestion_bp.route('/api/admin/reclassify', methods=['POST'])
def trigger_reclassify():
    """Wipe all theme assignments and reclassify against new 21 narrative themes.

    One-time admin endpoint — not for regular ingestion cycles.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Admin reclassification triggered")
    try:
        from app.services.theme_clustering import reclassify_all_articles
        result = reclassify_all_articles()
        return jsonify({
            "data": result,
            "meta": {
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Reclassification failed: {e}")
        return jsonify({
            "error": True,
            "message": str(e),
            "code": "RECLASSIFY_ERROR"
        }), 500
