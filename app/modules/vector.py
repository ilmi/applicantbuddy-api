import json


def add_resume_to_vector_db(resume_id: str, category: str, resume_text: str, **kwargs):
    import chromadb
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

    from app.core.settings import settings

    embedding_function = OpenAIEmbeddingFunction(
        api_key=settings.llm.OPENAI_API_KEY, model_name="text-embedding-3-small"
    )
    chroma_client = chromadb.PersistentClient(path="./chroma_db")

    collection = chroma_client.get_or_create_collection(
        name="resumes", embedding_function=embedding_function #type: ignore
    )
    collection.add(
        documents=[resume_text],
        metadatas=[{"resume_id": resume_id, "category": category, **kwargs}],
        ids=[resume_id],
    )


def query_resume_from_vector_db(
    query: str, n_results: int = 5, filter: dict | None = None
):
    from app.utils.vector_clients import chroma_client, embedding_function

    collection = chroma_client.get_collection(
        name="resumes", embedding_function=embedding_function #type: ignore
    )
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=filter,
    )
    return extract_resume_data(results)


def extract_resume_data(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    required_fields = ["documents", "distances", "metadatas"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    documents = data.get("documents", [])
    distances = data.get("distances", [])
    metadatas = data.get("metadatas", [])

    if not (len(documents) == len(distances) == len(metadatas)):
        raise ValueError(
            "documents, distances, and metadatas must have the same number of elements"
        )

    result = []

    for i in range(len(documents)):
        document_group = documents[i] if i < len(documents) else []
        distance_group = distances[i] if i < len(distances) else []
        metadata_group = metadatas[i] if i < len(metadatas) else []

        if not (len(document_group) == len(distance_group) == len(metadata_group)):
            raise ValueError(f"Mismatch in lengths for group {i}")

        for j in range(len(document_group)):
            result.append(
                {
                    "content": document_group[j],
                    "distance": float(distance_group[j]),
                    "metadata": metadata_group[j],
                }
            )

    return result
