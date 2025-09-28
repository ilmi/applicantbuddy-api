from celery import Celery

from app.core.settings import settings

app = Celery("tasks", broker=settings.database_settings.REDIS_URL, backend=settings.database_settings.REDIS_URL)
app.autodiscover_tasks(["app.tasks"])

from app.tasks import example_tasks  # noqa
