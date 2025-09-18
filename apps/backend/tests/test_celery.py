from app.workers import celery_app


def test_celery_configuration_defaults():
    assert celery_app.conf.timezone == 'UTC'
    assert 'purge-expired-schedules' in celery_app.conf.beat_schedule
    assert 'dispatch-schedules' in celery_app.conf.beat_schedule


def test_celery_tasks_registered():
    assert 'app.workers.tasks.maintenance.purge_expired_schedules' in celery_app.tasks
    assert 'app.workers.tasks.recordings.start_recording' in celery_app.tasks
    assert 'app.workers.tasks.schedules.dispatch' in celery_app.tasks
