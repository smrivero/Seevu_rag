from app.chunking import TokenChunker
from app.models import PageText


def test_chunker_stays_inside_each_page() -> None:
    chunker = TokenChunker(
        model="text-embedding-3-small",
        chunk_size=20,
        chunk_overlap=5,
    )
    pages = [
        PageText(page=1, text="alpha " * 40),
        PageText(page=2, text="bravo " * 40),
    ]
    chunks = chunker.chunk(pages, document_id="doc", filename="x.pdf")
    assert chunks
    assert {chunk.page for chunk in chunks} == {1, 2}
    for chunk in chunks:
        if chunk.page == 1:
            assert "bravo" not in chunk.text.lower()
        if chunk.page == 2:
            assert "alpha" not in chunk.text.lower()
        assert chunk.document_id == "doc"
        assert chunk.filename == "x.pdf"
        assert chunk.id == f"doc:{chunk.page}:{chunk.chunk_index}"


def test_chunker_skips_empty_pages() -> None:
    chunker = TokenChunker(
        model="text-embedding-3-small",
        chunk_size=50,
        chunk_overlap=10,
    )
    pages = [
        PageText(page=1, text="   "),
        PageText(page=2, text="kept text"),
    ]
    chunks = chunker.chunk(pages, document_id="doc", filename="x.pdf")
    assert len(chunks) == 1
    assert chunks[0].page == 2
    assert chunks[0].chunk_index == 0


def test_small_page_is_one_chunk() -> None:
    chunker = TokenChunker(
        model="text-embedding-3-small",
        chunk_size=600,
        chunk_overlap=100,
    )
    chunks = chunker.chunk(
        [PageText(page=1, text="short")],
        document_id="doc",
        filename="x.pdf",
    )
    assert len(chunks) == 1
    assert chunks[0].text == "short"
