from time import sleep
from app.tasks.celery_app import celery_app

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def process_document(self, document_id: int) -> dict:
    sleep(1)
    return {"document_id": document_id, "status": "processed"}

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def generate_embeddings(self, document_id: int) -> dict:
    sleep(1)
    return {"document_id": document_id, "status": "embedded"}

@celery_app.task
def send_notification(user_id: int, message: str) -> dict:
    return {"user_id": user_id, "sent": True, "message": message}

@celery_app.task
def cleanup_audit_logs() -> dict:
    return {"status": "completed"}

@celery_app.task
def generate_report(report_id: int) -> dict:
    return {"report_id": report_id, "status": "generated"}

@celery_app.task
def daily_analytics() -> dict:
    return {"status": "aggregated"}

@celery_app.task
def workflow_scheduler() -> dict:
    return {"status": "checked"}
