format:
	uv run ruff format .
	uv run ruff check . --fix

dev:
	uv run uvicorn app.main:app --reload

worker:
	uv run celery -A app.celery worker --pool=threads -c 2