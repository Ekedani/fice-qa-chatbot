from langchain_chroma import Chroma
from functools import lru_cache
from core.config import get_settings
from services.embeddings import get_embeddings


@lru_cache
def get_vectordb() -> Chroma:
    s = get_settings()

    return Chroma(
        persist_directory=s.chroma_dir,
        collection_name=s.chroma_collection,
        embedding_function=get_embeddings(),
    )
