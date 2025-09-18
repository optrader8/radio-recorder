from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL
backend_url = settings.CELERY_RESULT_BACKEND or broker_url

celery_app = Celery(
    "radio_recorder",
    broker=broker_url,
    backend=backend_url,
    include=[
        "app.workers.tasks.maintenance",
        "app.workers.tasks.recordings",
        "app.workers.tasks.schedules",
    ],
)

celery_app.conf.update(
    timezone="UTC",
    task_default_queue="default",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_always_eager=settings.ENVIRONMENT in {"development", "testing"},
    beat_schedule={
        "purge-expired-schedules": {
            "task": "app.workers.tasks.maintenance.purge_expired_schedules",
            "schedule": crontab(minute="*/30"),
        },
        "dispatch-schedules": {
            "task": "app.workers.tasks.schedules.dispatch",
            "schedule": crontab(minute="*"),
        },
    },
)

celery_app.autodiscover_tasks(['app.workers.tasks'])
