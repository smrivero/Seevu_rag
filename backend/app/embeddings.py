from collections.abc import Sequence
from typing import Protocol

from openai import OpenAI, OpenAIError

from app.errors import EmbeddingProviderError, MissingApiKeyError

_BATCH = 96


class EmbeddingProvider(Protocol):
    model: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        ...


class OpenAIEmbeddingProvider:
    def __init__(self, *, api_key: str, model: str) -> None:
        if not api_key.strip():
            raise MissingApiKeyError()
        self.model = model
        self._client = OpenAI(api_key=api_key)

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        try:
            for start in range(0, len(texts), _BATCH):
                batch = list(texts[start : start + _BATCH])
                response = self._client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
                ordered = sorted(response.data, key=lambda item: item.index)
                vectors.extend(item.embedding for item in ordered)
        except OpenAIError as exc:
            raise EmbeddingProviderError() from exc
        if len(vectors) != len(texts):
            raise EmbeddingProviderError()
        return vectors
