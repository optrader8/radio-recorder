from app.services.scheduler import run_schedule_dispatch
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.schedules.dispatch")
def dispatch_schedules_task() -> int:
    return run_schedule_dispatch()
