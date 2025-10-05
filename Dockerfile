FROM ghcr.io/astral-sh/uv:debian

WORKDIR /app

# Store the project virtualenv outside of the bind-mounted source tree so the
# container keeps its own Linux-specific environment even when the host mounts
# the repo into /app.
ENV UV_PROJECT_ENVIRONMENT=/usr/local/uv-env

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

CMD ["./bin/start.sh"]
