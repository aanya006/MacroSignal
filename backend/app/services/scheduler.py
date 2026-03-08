import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler = None


def run_scheduled_ingestion():
    """Wrapper for scheduled ingestion + clustering."""
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


def init_scheduler(app):
    """Initialize APScheduler with 30-minute ingestion cycle."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        run_scheduled_ingestion,
        'interval',
        minutes=30,
        id='news_ingestion',
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Scheduler started: ingestion every 30 minutes")
