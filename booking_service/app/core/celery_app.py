from celery import Celery

from app.core.config import settings


celery_app = Celery(
    'booking_service',
    broker=settings.redis_broker_url,
    include=['app.tasks.booking_tasks'],
)
