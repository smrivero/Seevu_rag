from app.config import Settings
from app.faiss_store import FAISSVectorStore
from app.store import VectorStore


def open_vector_store(settings: Settings) -> VectorStore:
    store = FAISSVectorStore(settings.index_dir)
    store.load()
    return store
