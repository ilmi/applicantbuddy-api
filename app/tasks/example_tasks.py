from loguru import logger

from app.celery import app


@app.task
def example_task():
    logger.info("Example Task")
