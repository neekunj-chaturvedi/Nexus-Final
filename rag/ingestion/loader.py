"""Loads Nexus knowledge-base markdown files and splits front matter from body.

Every document under rag/data/{policy_docs,product_docs,faqs,
communication_templates}/ starts with a small YAML front-matter block
(doc_id, category, product_line, tags, ...) — see rag/data/README.md.
This module turns each file into a RawDocument the chunker can consume.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
PROJECT_ROOT = DATA_ROOT.parent.parent
KNOWLEDGE_BASE_FOLDERS = ("policy_docs", "product_docs", "faqs", "communication_templates")
REQUIRED_FRONT_MATTER_FIELDS = ("doc_id", "category")

_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n?", re.DOTALL)


@dataclass(frozen=True)
class RawDocument:
    source_path: str
    metadata: dict
    content: str


def _split_front_matter(text: str) -> tuple[dict, str]:
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    front_matter = yaml.safe_load(match.group(1)) or {}
    return front_matter, text[match.end() :]


def load_knowledge_base(data_root: Path = DATA_ROOT) -> list[RawDocument]:
    """Load every markdown document from the four knowledge-base folders.

    A document missing a required front-matter field raises immediately —
    a malformed doc should fail loud at index-build time, not disappear
    from retrieval silently.
    """
    documents: list[RawDocument] = []

    for folder in KNOWLEDGE_BASE_FOLDERS:
        folder_path = data_root / folder
        if not folder_path.is_dir():
            continue

        for path in sorted(folder_path.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            front_matter, body = _split_front_matter(text)

            missing = [f for f in REQUIRED_FRONT_MATTER_FIELDS if f not in front_matter]
            if missing:
                raise ValueError(f"{path}: missing required front matter field(s) {missing}")

            documents.append(
                RawDocument(
                    source_path=str(path.relative_to(PROJECT_ROOT)),
                    metadata=front_matter,
                    content=body.strip(),
                )
            )

    return documents
