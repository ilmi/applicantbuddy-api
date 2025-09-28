from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.extended_settings.app_settings import AppSettings
from app.core.extended_settings.database_settings import DatabaseSettings
from app.core.extended_settings.llm_settings import LLMSettings
from app.core.extended_settings.logger_settings import LoggerSettings


class Settings(BaseSettings):
    app_settings: AppSettings = AppSettings()
    database_settings: DatabaseSettings = DatabaseSettings()
    llm_settings: LLMSettings = LLMSettings()
    logger: LoggerSettings = LoggerSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
