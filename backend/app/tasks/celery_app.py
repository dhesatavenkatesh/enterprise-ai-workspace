import os
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "enterprise_ai",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=["app.tasks.jobs"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.jobs.process_document": {"queue": "high_priority"},
        "app.tasks.jobs.generate_embeddings": {"queue": "high_priority"},
        "app.tasks.jobs.send_notification": {"queue": "default"},
        "app.tasks.jobs.generate_report": {"queue": "default"},
        "app.tasks.jobs.cleanup_audit_logs": {"queue": "low_priority"},
        "app.tasks.jobs.daily_analytics": {"queue": "low_priority"},
        "app.tasks.jobs.workflow_scheduler": {"queue": "default"},
    },
    beat_schedule={
        "daily-analytics": {
            "task": "app.tasks.jobs.daily_analytics",
            "schedule": crontab(hour=1, minute=0),
        },
        "audit-cleanup": {
            "task": "app.tasks.jobs.cleanup_audit_logs",
            "schedule": crontab(hour=2, minute=0, day_of_week="sunday"),
        },
        "workflow-scheduler": {
            "task": "app.tasks.jobs.workflow_scheduler",
            "schedule": 60.0,
        },
    },
)
