"""Builds and persists the Nexus knowledge-base index (§2.2 step 4, §3.3).

Pipeline: load_knowledge_base() -> chunk_documents() -> embed (OpenAI) ->
Chroma (persisted locally) + a chunks.jsonl snapshot the hybrid
retriever's BM25 side loads directly, so both retrievers always rank the
exact same chunk set.

Embeddings, model name, and store location all come from rag/config.py
(itself loaded from .env — see .env.example at the project root).

Run via the project-root entry point:
    python build_index.py [--rebuild]
"""

from __future__ import annotations

import argparse
import json
import shutil

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from rag.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    CHUNKS_PATH,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
    require_openai_api_key,
)

from .chunker import chunk_documents
from .loader import load_knowledge_base


def get_embeddings() -> OpenAIEmbeddings:
    require_openai_api_key()
    return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL, api_key=OPENAI_API_KEY)


def _persist_chunks_jsonl(chunks) -> None:
    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS_PATH.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps({"page_content": chunk.page_content, "metadata": chunk.metadata}) + "\n")


def build_index(rebuild: bool = False) -> dict:
    """Load -> chunk -> embed -> persist. Returns summary stats."""
    if rebuild and CHROMA_PERSIST_DIR.exists():
        shutil.rmtree(CHROMA_PERSIST_DIR)

    raw_documents = load_knowledge_base()
    chunks = chunk_documents(raw_documents)
    if not chunks:
        raise RuntimeError("No chunks produced from rag/data — is the knowledge base empty?")

    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=CHROMA_COLLECTION_NAME,
        persist_directory=str(CHROMA_PERSIST_DIR),
    )
    _persist_chunks_jsonl(chunks)

    return {
        "documents": len(raw_documents),
        "chunks": len(chunks),
        "vectorstore_dir": str(CHROMA_PERSIST_DIR),
        "chunks_path": str(CHUNKS_PATH),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Nexus RAG index")
    parser.add_argument("--rebuild", action="store_true", help="wipe the existing Chroma store first")
    args = parser.parse_args()

    stats = build_index(rebuild=args.rebuild)
    print(
        f"Indexed {stats['chunks']} chunks from {stats['documents']} documents "
        f"into {stats['vectorstore_dir']}"
    )


if __name__ == "__main__":
    main()
