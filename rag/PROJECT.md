# Nexus RAG — Unstructured Retrieval Module

This folder is the hybrid retrieval / grounding piece of the Nexus capstone
(spec §3.3 "Hybrid Retrieval & Grounding"). It is **only** the unstructured
half: semantic + keyword search over Meridian's policy wordings, product
fact sheets, FAQs, and communication templates. It does not touch
`meridian.db` or any MCP server — the orchestrator is responsible for
calling this module *and* the relevant MCP server for a request, then
reconciling the two (structured data wins on conflict — see
`data/README.md`).

## How it fits together

```
rag/data/*.md  (fake knowledge base, front-matter + markdown)
      |
      v  rag/ingestion/loader.py      — parses front matter + body
      v  rag/ingestion/chunker.py     — markdown-header split, then size-bound split
      v  rag/ingestion/index_builder.py
      |        |-- embeds chunks with OpenAI, persists to Chroma (rag/vectorstore/chroma)
      |        '-- snapshots the same chunks to rag/vectorstore/chunks.jsonl
      v
rag/retriever/hybrid_retriever.py
      |-- BM25Retriever   <- built from chunks.jsonl (keyword / exact-term search)
      |-- Chroma retriever <- built from vectorstore/chroma (semantic search)
      '-- EnsembleRetriever(BM25, Chroma)  <- fused hybrid ranking
      v
hybrid_search(query, k=5, product_line=None) -> [{"content": ..., "metadata": ...}, ...]
```

Everything below `rag/ingestion/` and `rag/retriever/` is a library — the
orchestrator (built elsewhere in the repo) calls `hybrid_search(...)` to
get grounded context, sanitises what comes back per §4 (retrieved
content is untrusted input, same as a RAG pipeline anywhere else), and
reconciles it against live MCP tool output before drafting a response.

## Folder structure

| Path | Purpose |
|---|---|
| `rag/data/` | The fake knowledge base itself — `policy_docs/`, `product_docs/`, `faqs/`, `communication_templates/`. See `rag/data/README.md` for what's in each file and which fixtures back the Showcase Scenario / Stress Tests. |
| `rag/ingestion/loader.py` | Reads every `.md` file, splits YAML front matter from the body. |
| `rag/ingestion/chunker.py` | Markdown-header-aware chunking (keeps section context), then size-bounded splitting (800 chars / 120 overlap). |
| `rag/ingestion/index_builder.py` | Runs the full pipeline: load → chunk → embed (OpenAI) → persist to Chroma + `chunks.jsonl`. |
| `rag/retriever/hybrid_retriever.py` | Builds the BM25 + Chroma `EnsembleRetriever` and exposes `hybrid_search()`. |
| `rag/config.py` | Single place all settings are read from `.env` — API key, embedding model, store paths, retriever weights/k. |
| `rag/vectorstore/` | **Generated, gitignored.** Chroma's persisted DB + the `chunks.jsonl` snapshot. Rebuild any time with `build_index.py`. |

## Setup

1. Install dependencies (root `requirements.txt` — this module needs the
   `langchain*`, `chromadb`, `openai`, and `rank-bm25` entries):

   ```bash
   pip install -r requirements.txt
   ```

2. Create your `.env` from the example and fill in a real OpenAI API key:

   ```bash
   copy .env.example .env
   ```

   Settings available (all optional except `OPENAI_API_KEY`; see
   `rag/config.py` for defaults):

   | Variable | Default | Meaning |
   |---|---|---|
   | `OPENAI_API_KEY` | *(required)* | Used for embeddings only — no OpenAI chat calls happen in this module. |
   | `OPENAI_EMBEDDING_MODEL` | `text-embedding-ada-002` | Chroma's own default OpenAI embedding model. |
   | `CHROMA_PERSIST_DIR` | `rag/vectorstore/chroma` | Where the vector store is written. |
   | `CHROMA_COLLECTION_NAME` | `nexus_knowledge_base` | Chroma collection name. |
   | `RETRIEVER_DEFAULT_K` | `5` | Default number of chunks returned per query. |
   | `RETRIEVER_BM25_WEIGHT` / `RETRIEVER_VECTOR_WEIGHT` | `0.4` / `0.6` | EnsembleRetriever fusion weights. |

## Running it

Build (or rebuild) the index — required before any query, and required
again any time a file under `rag/data/` changes:

```bash
python build_index.py
```

```bash
python build_index.py --rebuild    # wipes the old Chroma store first
```

Sanity-check retrieval from the command line:

```bash
python -m rag.retriever.hybrid_retriever "Can I set up auto-debit for my insurance premium from my savings account?"
```

Use it from code (this is what the orchestrator should call):

```python
from rag.retriever.hybrid_retriever import hybrid_search

hits = hybrid_search(
    "Can I set up auto-debit for my insurance premium from my savings account?",
    k=5,
    product_line="insurance",   # optional: "banking" | "insurance" | "wealth" | "cross_product" | None
)
for hit in hits:
    print(hit["metadata"]["doc_id"], hit["content"][:120])
```

`hybrid_search` returns raw, **unsanitised** chunk content — running it
through `guardrails.sanitize_free_text` / `sanitize_structure` before it
reaches an agent prompt or a customer is the caller's job (§4), not this
module's. One fixture document
(`rag/data/faqs/auto_debit_setup_community_notes.md`) exists specifically
to prove that guardrail catches injected content coming back from
retrieval — see its front matter for details.

## What's deliberately not here

- No LLM calls, no agents, no MCP clients. This module only answers "what
  does the unstructured knowledge base say," never "what should Nexus do
  about it."
- No reconciliation logic against structured MCP data — that's the
  orchestrator's hybrid-retrieval step (§3.3), which calls this module's
  `hybrid_search()` and a banking/insurance/wealth MCP tool, then decides
  which one wins on conflict.
- No `@trace(logger)` instrumentation yet — that depends on the shared
  `logging_config.py` module (§5), which isn't built yet. Once it exists,
  every public function here (`load_knowledge_base`, `chunk_documents`,
  `build_index`, `hybrid_search`) should get it, same as every other
  function in the codebase.
