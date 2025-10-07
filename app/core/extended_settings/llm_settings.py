from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENROUTER_API_KEY: str = "sk-not-provided"
    OPENROUTER_BASE_URL: str = "https://api.openai.com/v1/"

    MISTRAL_API_KEY: str = "sk-not-provided"
