from datetime import datetime, timezone

from app.core.logging import get_logger
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.workers.tasks.maintenance.purge_expired_schedules")
def purge_expired_schedules() -> str:
    """Placeholder task that will prune expired schedules once implemented."""
    logger.info("Purging expired schedules placeholder executed at %s", datetime.now(timezone.utc))
    return "scheduled"
