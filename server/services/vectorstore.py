from langchain_chroma import Chroma
from functools import lru_cache
from core.config import get_settings
from services.embeddings import get_embeddings


@lru_cache
def get_vectordb() -> Chroma:
    settings = get_settings()

    return Chroma(
        persist_directory=settings.chroma_directory,
        collection_name=settings.chroma_collection,
        embedding_function=get_embeddings(),
    )
