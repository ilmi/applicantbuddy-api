from sqlmodel import Session, create_engine

from app.core.settings import settings

engine = create_engine(settings.database_settings.DATABASE_URL)


def db_session():
    with Session(engine) as session:
        yield session
