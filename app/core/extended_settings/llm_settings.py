from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Large Language Model API settings"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    MISTRAL_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
