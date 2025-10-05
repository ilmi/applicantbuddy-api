#!/bin/bash
set -e #Exit on any error

echo "🚀 Running database migration ..."
uv run alembic upgrade head

echo "🚀 Starting FastAPI server ..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
