import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from app.core.settings import settings

embedding_function = OpenAIEmbeddingFunction(
    api_key=settings.llm.OPENAI_API_KEY, model_name="text-embedding-3-small"
)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
