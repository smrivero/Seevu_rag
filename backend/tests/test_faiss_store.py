from app.faiss_store import FAISSVectorStore
from app.models import Chunk
from tests.fakes import FakeEmbeddings


def test_search_returns_added_chunk(tmp_path) -> None:
    store = FAISSVectorStore(tmp_path)
    embeddings = FakeEmbeddings(dimension=8)
    chunk = Chunk(
        id="doc:1:0",
        document_id="doc",
        filename="a.pdf",
        page=1,
        chunk_index=0,
        text="unique phrase about widgets",
    )
    vectors = embeddings.embed([chunk.text])
    store.add([chunk], vectors)
    store.save()
    store.load()
    hits = store.search(vectors[0], limit=1)
    assert hits[0].chunk_id == chunk.id
    assert hits[0].page == 1
    assert hits[0].score > 0
