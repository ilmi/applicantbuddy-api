from mistralai import Mistral
from openai import OpenAI

from app.core.settings import settings

mistral_client = Mistral(api_key=settings.llm_settings.MISTRAL_API_KEY)

openai_client = OpenAI(
    api_key=settings.llm_settings.OPENROUTER_API_KEY,
    base_url=settings.llm_settings.OPENROUTER_BASE_URL,
)
