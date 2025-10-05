from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.extended_settings.app_settings import AppSettings
from app.core.extended_settings.cors import CORSSettings
from app.core.extended_settings.database_settings import DatabaseSettings
from app.core.extended_settings.llm_settings import LLMSettings
from app.core.extended_settings.logger_settings import LoggerSettings


class Settings(BaseSettings):
    app_settings: AppSettings = AppSettings()
    database_settings: DatabaseSettings = DatabaseSettings()
    cors: CORSSettings = CORSSettings()
    llm: LLMSettings = LLMSettings()
    logger: LoggerSettings = LoggerSettings()

    HASHING_SECRET_KEY: str = "secret-key"
    HASHING_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_TOKEN_EXPIRED: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
