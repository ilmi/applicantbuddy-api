from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.core.settings import settings
from app.router.example_router import example_router

settings.logger.setup_logger()


app = FastAPI(
    title=settings.app_settings.APP_NAME,
    version=settings.app_settings.VERSION,
    description=settings.app_settings.DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app_settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.app_settings.ALLOW_METHODS,
    allow_headers=settings.app_settings.ALLOW_HEADERS,
)

app.include_router(example_router)

if settings.app_settings.DEBUG:
    from fastapi.staticfiles import StaticFiles

    app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/scalar", include_in_schema=False)
def read_scalar():
    return get_scalar_api_reference(
        title=settings.app_settings.APP_NAME,
        openapi_url="/openapi.json",
    )
