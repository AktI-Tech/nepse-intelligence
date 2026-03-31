"""Scheduled tasks for NEPSE data pipeline."""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.pipeline import get_pipeline

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_pipeline_task():
    """Task to run the data pipeline."""
    try:
        pipeline = get_pipeline()
        result = pipeline.run_once()
        if result["status"] == "success":
            logger.info(f"Pipeline task completed: {result}")
        else:
            logger.error(f"Pipeline task failed: {result}")
    except Exception as e:
        logger.error(f"Pipeline task error: {e}")


def start_scheduler():
    """Start background scheduler for pipeline tasks."""
    if scheduler.running:
        return

    # Run pipeline every 5 minutes
    scheduler.add_job(
        run_pipeline_task,
        trigger=IntervalTrigger(minutes=5),
        id="nepse_pipeline",
        name="NEPSE Data Pipeline",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started: NEPSE pipeline will run every 5 minutes")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
