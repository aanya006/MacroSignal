import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler = None


def run_scheduled_ingestion():
    """Wrapper for scheduled ingestion + clustering + causal chain generation."""
    logger.info("Scheduled ingestion cycle starting...")
    try:
        from app.services.news_ingestion import run_ingestion
        result = run_ingestion()
        logger.info(
            f"Scheduled ingestion complete: "
            f"fetched={result['articles_fetched']}, "
            f"new={result['articles_new']}, "
            f"themes={result['themes_updated']}"
        )
    except Exception as e:
        logger.error(f"Scheduled ingestion failed: {e}")

    try:
        from app.services.causal_chain import generate_chains_for_hot_themes
        generated = generate_chains_for_hot_themes()
        logger.info(f"Causal chain generation complete: {generated} chains updated")
    except Exception as e:
        logger.error(f"Causal chain generation failed: {e}")


def init_scheduler(app):
    """Initialize APScheduler with twice-daily ingestion cycle (every 12 hours)."""
    from app.utils.config import INGESTION_ENABLED

    if not INGESTION_ENABLED:
        logger.info("Scheduler skipped: INGESTION_ENABLED is false")
        return

    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_scheduled_ingestion,
        'interval',
        hours=12,
        id='news_ingestion',
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started: ingestion every 12 hours")
