from pathlib import Path

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    vector_store: str = "faiss"
    chunk_size: int = 600
    chunk_overlap: int = 100
    max_upload_bytes: int = 10_485_760
    index_dir: Path = Path("data/index")
    log_level: str = "INFO"

    @field_validator("chunk_overlap")
    @classmethod
    def overlap_smaller_than_size(cls, overlap: int, info: ValidationInfo) -> int:
        size = info.data.get("chunk_size", 600)
        if overlap < 0:
            raise ValueError("CHUNK_OVERLAP must be >= 0")
        if overlap >= size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        return overlap

    @field_validator("vector_store")
    @classmethod
    def known_store(cls, value: str) -> str:
        if value != "faiss":
            raise ValueError("VECTOR_STORE must be faiss in this milestone")
        return value
