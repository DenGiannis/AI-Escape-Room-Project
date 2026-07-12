from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_documents() -> list[Document]:
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    docs: list[Document] = []
    for md_file in sorted(DATA_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        chunks = splitter.create_documents(
            [text],
            metadatas=[{"source": md_file.name}],
        )
        docs.extend(chunks)
    return docs


@lru_cache(maxsize=1)
def get_retriever():
    docs = _load_documents()
    vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY))
    return vectorstore.as_retriever(search_kwargs={"k": 4})


@lru_cache(maxsize=1)
def _get_vectorstore() -> FAISS:
    docs = _load_documents()
    return FAISS.from_documents(docs, OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY))


def retrieve(query: str) -> str:
    """Return relevant game knowledge as a single string, for use by the agent."""
    docs = get_retriever().invoke(query)
    return "\n\n---\n\n".join(d.page_content for d in docs)


_PLAYER_SAFE_SOURCES = {
    "world_lore.md",
    "rooms.md",
    "items.md",
    "athena_character.md",
}


def retrieve_player_safe(query: str, k: int = 4) -> str:
    """Retrieve knowledge for player-facing answers, EXCLUDING puzzles.md.

    The lore/Q&A tool is exposed to the player through Athena, so puzzle solutions and
    hint reveals (which live in puzzles.md) must never leak through it. We over-fetch,
    drop any puzzles.md chunks, then keep the top k of what remains.
    """
    vectorstore = _get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k * 3)
    safe = [d for d in docs if d.metadata.get("source") in _PLAYER_SAFE_SOURCES]
    chosen = safe[:k] if safe else docs[:k]
    return "\n\n---\n\n".join(d.page_content for d in chosen)


def retrieve_filtered(query: str, source: str, k: int = 4) -> str:
    """Return relevant chunks restricted to a single source markdown file (e.g. 'puzzles.md').

    Falls back to an unfiltered search if the filtered search returns nothing, so a
    missing/renamed source file never leaves the caller with an empty context.
    """
    vectorstore = _get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k, filter={"source": source})
    if not docs:
        docs = vectorstore.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content for d in docs)
