## Why

Taiwan formally entered the carbon pricing era in 2025 with the enforcement of the Climate Change Response Act and the launch of carbon fee regulations via the Taiwan Carbon Solution Exchange (TCX). This project solves the problem of tracking rapidly evolving regulations by building a domain-specific RAG system. It aggregates official policy documents, regulations, and market data into a structured knowledge base to enable accurate, context-aware Q&A.

## What Changes

- Build a reproducible data ingestion pipeline to load raw policy files, clean and chunk them by structural boundaries (e.g., articles/sections), embed them, and index them. (Owned by `PDFProcessor`, `ChunkStrategy`, and `VectorStore`)
- Implement a CLI query interface that supports source-cited output and applies jurisdiction-specific context to prevent cross-standard confusion. (Owned by `RAGQuery`)
- Implement an automated synthesizer to generate a domain expert `skill.md` reference for AI agents based on the collected knowledge. (Owned by `SkillBuilder`)

## Capabilities

### New Capabilities
- `data-ingestion`: Manages incremental document preprocessing, table-to-text conversion, structural chunking (e.g. 第X條 boundaries), valid_date metadata tracking, and local embedding into a ChromaDB vector store.
- `rag-query`: Provides an interactive CLI tool for querying the knowledge base using structured prompt framing over LiteLLM (gemini-2.5-flash / gpt-oss-20b), returning answers with clear citations to official sources.
- `skill-builder`: Automates the generation of a comprehensive `skill.md` covering core concepts (carbon fee, CBAM), entities, and status derived from RAG responses.

### Modified Capabilities


## Non-goals

- No graphical user interfaces or web apps; all components operate via the CLI.
- No remote embedding APIs; embeddings rely strictly on local models (`sentence-transformers`) to prevent external vendor dependencies.
- No generalization to a universal RAG framework; intentionally heavily coupled to Taiwan's specific jurisdiction and regulatory structures.

## Impact

- Introduces new core libraries: `src/processor.py`, `src/chunker.py`, `src/store.py`, `src/query.py`, and `src/builder.py`.
- Introduces three new CLI entrypoints: `data_update.py`, `rag_query.py`, and `skill_builder.py`.
- Impacts project dependencies by adding `chromadb` (or pgvector), `sentence-transformers`, `litellm`, and `pdfplumber`.
- Will generate local persistent data storage for ChromaDB.
