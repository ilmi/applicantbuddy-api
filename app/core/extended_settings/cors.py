from pydantic_settings import BaseSettings, SettingsConfigDict


class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="CORS_", extra="ignore"
    )
