from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.settings import settings
from app.router.auth_router import auth_router

settings.logger.setup_logger()

app = FastAPI(
    title=settings.app_settings.APP_NAME,
    version=settings.app_settings.VERSION,
    description=settings.app_settings.DESCRIPTION,
)

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.database_settings.REDIS_URL)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.app_settings.ALLOW_METHODS,
    allow_headers=settings.app_settings.ALLOW_HEADERS,
)

app.include_router(auth_router)

if settings.app_settings.DEBUG:
    from fastapi.staticfiles import StaticFiles

    app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/scalar", include_in_schema=False)
def read_scalar():
    return get_scalar_api_reference(
        title=settings.app_settings.APP_NAME,
        openapi_url="/openapi.json",
    )
