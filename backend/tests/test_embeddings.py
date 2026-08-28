import pytest

from app.errors import MissingApiKeyError
from app.embeddings import OpenAIEmbeddingProvider
from tests.fakes import assert_never_openai


def test_empty_api_key_does_not_construct_openai(monkeypatch) -> None:
    assert_never_openai(monkeypatch)
    with pytest.raises(MissingApiKeyError):
        OpenAIEmbeddingProvider(api_key="   ", model="text-embedding-3-small")
