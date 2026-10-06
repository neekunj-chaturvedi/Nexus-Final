"""Entry point: build the local RAG knowledge-base index (see §2.2 step 4).

Usage:
    python build_index.py [--rebuild]
"""

from rag.ingestion.index_builder import main

if __name__ == "__main__":
    main()
