## Why
Taiwan formally entered the carbon pricing era in 2025 with the enforcement of the Climate Change Response Act and the launch of carbon fee regulations, while the Taiwan Carbon Solution Exchange (TCX) was established in 2023. A localized Retrieval-Augmented Generation (RAG) system is needed to aggregate official policy documents, regulations, and market data to enable structured Q&A over this rapidly evolving domain.

## What Changes
- Introduce a systematic pipeline to collect and embed 20+ public official documents covering carbon fees, credits, CBAM, and voluntary reduction schemes into a local vector store.
- Implement a structured RAG query flow using local embeddings and LiteLLM to interface with standard models, ensuring robust jurisdiction framing.
- Create an automated skill builder to synthesize key domain knowledge into a comprehensive reference manual for AI agents.

## Capabilities

### New Capabilities
- `data-update`: A system to load, validate, chunk by structural entity, embed, and index documents directly into ChromaDB/pgvector, supporting both full wipe/reindex and incremental updates via hash matching.
- `rag-query`: A CLI interface for querying the vector store with cited source outputs and domain-specific context framing.
- `skill-builder`: An automated generator that consolidates findings and Q&A into a unified `skill.md` domain expert reference organized by core domain concepts.

### Modified Capabilities
- (None)

## Impact
- New Python system requiring `sentence-transformers`, `chromadb` (or `pgvector`), and `litellm` dependencies.
- Will persist data locally in vector database format, and will rely on externally fetched pdfs.
