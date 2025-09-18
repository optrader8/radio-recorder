from app.workers.celery_app import celery_app
from app.services.recording_engine import run_recording_task


@celery_app.task(name="app.workers.tasks.recordings.start_recording")
def start_recording_task(recording_id: str) -> str:
    return run_recording_task(recording_id)
