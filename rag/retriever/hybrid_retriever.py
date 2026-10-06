"""Hybrid (sparse + dense) retrieval over the Nexus knowledge base (§3.3).

Combines a BM25 keyword retriever with a Chroma dense-vector retriever
(OpenAI embeddings) through LangChain's EnsembleRetriever, so a query
that hits on exact terms (product/scenario tags, IDs) and a query that
needs semantic matching (paraphrased customer language) both get a fair
shot at surfacing the right chunk.

All settings (API key, embedding model, store location, retriever
weights/k) come from rag/config.py, loaded from .env.

Requires the index to already exist — run `python build_index.py` first.
"""

from __future__ import annotations

import json
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from rag.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    CHUNKS_PATH,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    RETRIEVER_BM25_WEIGHT,
    RETRIEVER_DEFAULT_K,
    RETRIEVER_VECTOR_WEIGHT,
    require_openai_api_key,
)


class IndexNotBuiltError(RuntimeError):
    """Raised when the retriever is used before build_index.py has run."""


def _require(path):
    if not path.exists():
        raise IndexNotBuiltError(
            f"{path} not found — run `python build_index.py` first."
        )
    return path


@lru_cache(maxsize=1)
def _load_chunks() -> list[Document]:
    chunks = []
    with _require(CHUNKS_PATH).open(encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            chunks.append(
                Document(
                    page_content=record["page_content"], metadata=record["metadata"]
                )
            )
    return chunks


@lru_cache(maxsize=1)
def _get_embeddings() -> OpenAIEmbeddings:
    require_openai_api_key()
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL, api_key=OPENAI_API_KEY)


@lru_cache(maxsize=1)
def _get_vectorstore() -> Chroma:
    _require(CHROMA_PERSIST_DIR)
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=str(CHROMA_PERSIST_DIR),
    )


@lru_cache(maxsize=1)
def _get_bm25_retriever() -> BM25Retriever:
    return BM25Retriever.from_documents(_load_chunks())


def get_hybrid_retriever(k: int = RETRIEVER_DEFAULT_K) -> EnsembleRetriever:
    """The raw LangChain EnsembleRetriever (BM25 + Chroma), for direct .invoke() use."""
    bm25 = _get_bm25_retriever()
    bm25.k = k
    vector_retriever = _get_vectorstore().as_retriever(search_kwargs={"k": k})
    return EnsembleRetriever(
        retrievers=[bm25, vector_retriever],
        weights=[RETRIEVER_BM25_WEIGHT, RETRIEVER_VECTOR_WEIGHT],
    )


def _matches_product_line(metadata: dict, product_line: str | None) -> bool:
    if product_line is None:
        return True
    return metadata.get("product_line") in (product_line, "cross_product", "all")


def hybrid_search(
    query: str, k: int = RETRIEVER_DEFAULT_K, product_line: str | None = None
) -> list[dict]:
    """Retrieve the top-k knowledge-base chunks for a query.

    product_line, if given, filters the ensemble's ranked results to that
    product line plus any cross_product/all document. Filtering happens
    *after* ensemble ranking — BM25 has no native metadata filter, and
    ranking quality should come from the fused BM25+vector scores, not a
    pre-filter applied to only one retriever.
    """
    fetch_k = k * 3 if product_line else k
    retriever = get_hybrid_retriever(k=fetch_k)
    results = retriever.invoke(query)

    filtered = [
        doc for doc in results if _matches_product_line(doc.metadata, product_line)
    ][:k]

    return [{"content": doc.page_content, "metadata": doc.metadata} for doc in filtered]


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or (
        "Can I set up auto-debit for my insurance premium from my savings account, "
        "and is auto-debit actually covered under my policy's payment terms?"
    )
    print(f"Query: {query}\n")
    for i, hit in enumerate(hybrid_search(query, k=5), start=1):
        meta = hit["metadata"]
        print(f"[{i}] doc_id={meta.get('doc_id')} section={meta.get('section')!r}")
        print(hit["content"][:300].replace("\n", " "))
        print()
