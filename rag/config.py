"""Centralised environment configuration for the Nexus RAG pipeline.

Loads a local .env file (copy .env.example at the project root to .env
and fill in real values) and exposes every setting the index builder and
the hybrid retriever need, so there's exactly one place that reads from
the environment.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RAG_ROOT = Path(__file__).resolve().parent

# --- OpenAI embeddings ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# text-embedding-ada-002 is chromadb's own OpenAIEmbeddingFunction default model.
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")

# --- Local Chroma vector store ---
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(RAG_ROOT / "vectorstore" / "chroma")))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "nexus_knowledge_base")
CHUNKS_PATH = CHROMA_PERSIST_DIR.parent / "chunks.jsonl"

# --- Hybrid retriever tuning ---
RETRIEVER_DEFAULT_K = int(os.getenv("RETRIEVER_DEFAULT_K", "5"))
RETRIEVER_BM25_WEIGHT = float(os.getenv("RETRIEVER_BM25_WEIGHT", "0.4"))
RETRIEVER_VECTOR_WEIGHT = float(os.getenv("RETRIEVER_VECTOR_WEIGHT", "0.6"))


def require_openai_api_key() -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and fill in a real key."
        )
    return OPENAI_API_KEY
