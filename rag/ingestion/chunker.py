"""Markdown-aware chunking for the Nexus knowledge base (§3.3 retrieval).

Splits each document on its markdown headers first, so a chunk keeps the
section it came from (e.g. "Premium Payment Terms") in its metadata, then
bounds chunk size with a recursive character splitter. Every chunk
inherits the source document's front-matter metadata plus a stable
chunk_id, so a retrieved hit can always be traced back to doc_id + section.
"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from .loader import RawDocument

HEADERS_TO_SPLIT_ON = [("#", "h1"), ("##", "h2"), ("###", "h3")]
HEADER_LEVELS = tuple(level for _, level in HEADERS_TO_SPLIT_ON)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

_header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON, strip_headers=False)
_char_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


def _flatten_metadata_value(value):
    """Chroma metadata values must be str/int/float/bool — flatten lists."""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def chunk_document(raw: RawDocument) -> list[Document]:
    """Split one knowledge-base document into retrieval-sized chunks."""
    doc_metadata = {k: _flatten_metadata_value(v) for k, v in raw.metadata.items()}
    doc_id = doc_metadata.get("doc_id", raw.source_path)

    chunks: list[Document] = []
    chunk_index = 0

    for section in _header_splitter.split_text(raw.content):
        header_path = " > ".join(
            section.metadata[level] for level in HEADER_LEVELS if section.metadata.get(level)
        )

        for piece in _char_splitter.split_text(section.page_content):
            if not piece.strip():
                continue

            metadata = {
                **doc_metadata,
                "source_path": raw.source_path,
                "section": header_path,
                "chunk_id": f"{doc_id}::chunk-{chunk_index}",
            }
            chunks.append(Document(page_content=piece, metadata=metadata))
            chunk_index += 1

    return chunks


def chunk_documents(raw_documents: list[RawDocument]) -> list[Document]:
    chunks: list[Document] = []
    for raw in raw_documents:
        chunks.extend(chunk_document(raw))
    return chunks
