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


def retrieve(query: str) -> str:
    """Return relevant game knowledge as a single string, for use by the agent."""
    docs = get_retriever().invoke(query)
    return "\n\n---\n\n".join(d.page_content for d in docs)
