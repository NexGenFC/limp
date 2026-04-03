from celery import shared_task


@shared_task(bind=True, max_retries=3)
def celery_heartbeat(self) -> str:
    return "ok"
