import hashlib
from collections.abc import Sequence

from app.embeddings import EmbeddingProvider


class FakeEmbeddings:
    model = "text-embedding-3-small"
    calls: list[tuple[str, ...]]

    def __init__(self, dimension: int = 8) -> None:
        self.dimension = dimension
        self.calls = []

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls.append(tuple(texts))
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            raw = [(digest[i % len(digest)] / 255.0) for i in range(self.dimension)]
            vectors.append(raw)
        return vectors


def assert_never_openai(monkeypatch) -> None:
    def blocked(*_args, **_kwargs):
        raise AssertionError("OpenAI client must not be constructed in tests")

    monkeypatch.setattr("app.embeddings.OpenAI", blocked)
    monkeypatch.setattr("app.main.OpenAIEmbeddingProvider", blocked)
