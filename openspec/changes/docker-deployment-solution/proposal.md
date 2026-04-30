## Why

The project currently depends on local Python, Node, model, and vector database setup, which makes deployment fragile across Windows, Linux, and future hosting environments. A Docker deployment solution will provide a repeatable way to run the RAG backend, background indexing/runtime processes, and the React frontend with explicit environment and volume boundaries.

## What Changes

- Add a Docker-based deployment path for the existing RAG system, including Python dependencies, ChromaDB persistence, and runtime environment variables.
- Add a backend service container that serves the chat API and owns RAG query execution through `RAGQuery` and `VectorStore`.
- Add a frontend service container that builds and serves the React chat interface.
- Add a background-capable runtime path for indexing or maintenance commands such as `data_update.py --rebuild` without mixing those jobs into the frontend service.
- Add deployment documentation and examples for local Docker Compose startup.
- Preserve existing `.pdf`, `.txt`, `.md`, and `.html` ingestion behavior; `ProcessorFactory` continues to own file-format routing, and the format-specific processor classes continue to own extraction.

## Capabilities

### New Capabilities

- `docker-deployment`: Covers containerized deployment for the RAG backend, background jobs, frontend interface, environment configuration, persistent data volumes, and local orchestration.

### Modified Capabilities

- None.

## Non-goals

- Replace the existing CLI workflows for `data_update.py`, `rag_query.py`, or `skill_builder.py`.
- Change retrieval, chunking, embedding, or prompt behavior in `RAGQuery`, `VectorStore`, `ChunkStrategy`, or document processors.
- Add production cloud infrastructure such as Kubernetes, Terraform, managed databases, or CI/CD deployment pipelines.
- Change the supported ingestion formats beyond the existing `.pdf`, `.txt`, `.md`, and `.html` processors.

## Impact

- Affected code and configuration: Dockerfiles, Docker Compose configuration, backend startup scripts or entrypoints, frontend build/runtime configuration, README deployment instructions, and environment variable examples.
- Affected runtime systems: Python RAG backend, ChromaDB persistence directory, React frontend, background indexing process, and local developer deployment workflow.
- Ownership boundaries: `RAGQuery` owns answer generation, `VectorStore` owns ChromaDB and BM25 retrieval, `data_update.py` owns ingestion orchestration, `ProcessorFactory` owns document processor selection, format processors own `.pdf`, `.txt`, `.md`, and `.html` extraction, and the Docker/Compose layer owns service wiring and persistence.
