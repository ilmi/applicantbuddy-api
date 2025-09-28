# FastAPI Template

A production-ready FastAPI template with modern Python development practices, database integration, background tasks, and comprehensive tooling.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs with Python 3.12+
- **Database Integration**: PostgreSQL with SQLModel ORM and Alembic migrations
- **Background Tasks**: Celery with Redis broker for asynchronous task processing
- **API Documentation**: Automatic OpenAPI documentation with Scalar UI
- **Configuration Management**: Pydantic Settings with environment variable support
- **Code Quality**: Ruff for linting and formatting
- **Development Tools**: Hot reload, CORS middleware, static file serving
- **LLM Integration**: Built-in support for OpenAI and Mistral APIs

## Tech Stack

- **Framework**: FastAPI 0.116.1+
- **Database**: PostgreSQL with SQLModel
- **Task Queue**: Celery with Redis
- **Migration**: Alembic
- **Validation**: Pydantic
- **Code Quality**: Ruff
- **Server**: Uvicorn (development) / Gunicorn (production)
- **Documentation**: Scalar FastAPI

## Project Structure

```
fastapi-template/
├── app/
│   ├── core/
│   │   ├── extended_settings/
│   │   │   ├── app_settings.py      # Application configuration
│   │   │   ├── database_settings.py # Database and Redis settings
│   │   │   └── llm_settings.py      # LLM API configurations
│   │   ├── models.py                # Base SQLModel classes
│   │   └── settings.py              # Main settings aggregator
│   ├── database/
│   │   ├── engine.py                # Database engine setup
│   │   └── models.py                # Database models
│   ├── router/
│   │   └── example_router.py        # API route definitions
│   ├── services/                    # Business logic services
│   ├── tasks/
│   │   └── example_tasks.py         # Celery background tasks
│   ├── utils/
│   │   └── generate_ids.py          # Utility functions
│   ├── celery.py                    # Celery configuration
│   └── main.py                      # FastAPI application entry point
├── .files/                          # Deployment configuration files
│   ├── nginx-domain.com             # Nginx reverse proxy configuration
│   ├── service-api.service          # Systemd service for FastAPI app
│   └── service-worker.service       # Systemd service for Celery worker
├── alembic/                         # Database migration files
├── bin/                             # Setup and deployment scripts
│   ├── setup.sh                     # Initial project setup script
│   └── update.sh                    # Production update script
├── public/                          # Static files directory
├── pyproject.toml                   # Project dependencies and configuration
├── alembic.ini                      # Alembic configuration
└── Makefile                         # Development commands
```

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- UV package manager (recommended)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd fastapi-template
```

2. Install dependencies:

```bash
uv sync
```

3. Create environment file:

```bash
cp .env.example .env
```

4. Configure your environment variables in `.env`:

```env
# Application Settings
APP_NAME=FastAPI Template
VERSION=0.1.0
DESCRIPTION=FastAPI Template API
DEBUG=true

# Database Settings
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=postgres

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# LLM Settings
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1/

# Logger Settings (optional - defaults will be used if not specified)
LOGGER_LEVEL=INFO
LOGGER_FILE_ENABLED=true
LOGGER_FILE_PATH=logs/app.log
LOGGER_CONSOLE_ENABLED=true
```

5. Run database migrations:

```bash
uv run alembic upgrade head
```

### Development

Start the development server:

```bash
make dev
# or
uv run uvicorn app.main:app --reload
```

Start the Celery worker:

```bash
make worker
# or
uv run celery -A app.celery worker --pool=threads -c 2
```

### Code Quality

Format and lint code:

```bash
make format
# or
uv run ruff format .
uv run ruff check . --fix
```

## Configuration

The application uses a modular configuration system with four main settings classes:

### App Settings (`app_settings.py`)

- `APP_NAME`: Application name
- `VERSION`: Application version
- `DESCRIPTION`: Application description
- `DEBUG`: Debug mode toggle
- `ALLOW_ORIGINS`: CORS allowed origins
- `ALLOW_METHODS`: CORS allowed methods
- `ALLOW_HEADERS`: CORS allowed headers

### Database Settings (`database_settings.py`)

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: PostgreSQL connection
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`: Redis connection
- Auto-generated `DATABASE_URL` and `REDIS_URL` properties

### LLM Settings (`llm_settings.py`)

- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_BASE_URL`: OpenAI API base URL (default: https://api.openai.com/v1/)

### Logger Settings (`logger_settings.py`)

- `LOGGER_LEVEL`: Log level (default: INFO)
- `LOGGER_FILE_ENABLED`: Enable file logging (default: true)
- `LOGGER_FILE_PATH`: Log file path (default: logs/app.log)
- `LOGGER_FILE_ROTATION`: Log file rotation (default: 10 MB)
- `LOGGER_FILE_RETENTION`: Log file retention (default: 30 days)
- `LOGGER_CONSOLE_ENABLED`: Enable console logging (default: true)
- `LOGGER_CONSOLE_COLORIZE`: Colorize console output (default: true)

## API Documentation

Once the server is running, you can access:

- **Scalar Documentation**: `http://localhost:8000/scalar`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
- **Example Endpoint**: `http://localhost:8000/example/`

## Database Models

The template includes a base model with common fields:

```python
class BaseModel(SQLModel):
    id: str = Field(default_factory=generate_id, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_deleted: bool = Field(default=False)
```

## Background Tasks

Celery is configured for background task processing. Tasks are auto-discovered from the `app.tasks` module.

## Development Guidelines

- Follow the existing project structure
- Use type hints throughout the codebase
- Run `make format` before committing
- Add tests for new features
- Update documentation as needed

## Production Deployment

The template includes production-ready deployment configurations:

### Quick Setup

1. Run the setup script:

```bash
./bin/setup.sh
```

2. Configure environment variables for production:

```bash
cp .env.example .env
# Edit .env with production values
```

3. Set up systemd services:

```bash
# Copy service files to systemd directory
sudo cp .files/service-api.service /etc/systemd/system/
sudo cp .files/service-worker.service /etc/systemd/system/

# Edit service files to match your paths and user
sudo systemctl daemon-reload
sudo systemctl enable service-api.service
sudo systemctl enable service-worker.service
sudo systemctl start service-api.service
sudo systemctl start service-worker.service
```

4. Configure Nginx (optional):

```bash
# Copy and modify nginx configuration
sudo cp .files/nginx-domain.com /etc/nginx/sites-available/your-domain
# Edit the file to match your domain
sudo ln -s /etc/nginx/sites-available/your-domain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Production Updates

Use the update script for seamless deployments:

```bash
./bin/update.sh
```

### Deployment Files

- **`.files/nginx-domain.com`**: Nginx reverse proxy configuration
- **`.files/service-api.service`**: Systemd service for the FastAPI application
- **`.files/service-worker.service`**: Systemd service for Celery background workers
- **`bin/setup.sh`**: Automated setup script that installs uv, dependencies, and runs migrations
- **`bin/update.sh`**: Production update script that pulls changes, syncs dependencies, and restarts services

### Production Checklist

1. Set `DEBUG=false` in environment variables
2. Configure proper PostgreSQL and Redis instances
3. Set up proper logging and monitoring
4. Configure SSL certificates for HTTPS
5. Set appropriate user permissions for service files
6. Monitor application logs via systemd journals

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For questions and support, please open an issue in the repository.
