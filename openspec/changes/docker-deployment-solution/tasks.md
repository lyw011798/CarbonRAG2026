## 1. Backend Runtime

- [x] 1.1 Add or finalize one HTTP backend entrypoint function for `/health` and `POST /chat`.
- [x] 1.2 Wire the backend entrypoint to `RAGQuery` for answer generation.
- [x] 1.3 Wire the backend entrypoint to `VectorStore` using `CHROMA_PERSIST_DIR`.
- [x] 1.4 Add explicit backend errors for missing environment variables, missing index data, and failed query execution.
- [x] 1.5 Add a backend Dockerfile using a supported Python runtime.

## 2. Frontend Runtime

- [x] 2.1 Add a production frontend Dockerfile for the Vite React app.
- [x] 2.2 Configure the frontend runtime to route chat requests to the backend service.
- [x] 2.3 Verify the frontend production build serves the chat interface over HTTP.

## 3. Compose Deployment

- [x] 3.1 Add `docker-compose.yml` with separate backend and frontend services.
- [x] 3.2 Add an indexing service or profile that runs `data_update.py`.
- [x] 3.3 Configure Compose volumes or bind mounts for `data/raw`, `data/processed`, `db/chroma`, and model caches.
- [x] 3.4 Configure Compose environment loading from `.env`.
- [x] 3.5 Add service health checks for backend and frontend startup verification.

## 4. Ingestion Compatibility

- [x] 4.1 Verify `PDFProcessor` can process `.pdf` inputs from the mounted raw data path inside Docker.
- [x] 4.2 Verify `TextProcessor` can process `.txt` inputs from the mounted raw data path inside Docker.
- [x] 4.3 Verify `MarkdownProcessor` can process `.md` inputs from the mounted raw data path inside Docker.
- [x] 4.4 Verify `HTMLProcessor` can process `.html` inputs from the mounted raw data path inside Docker.
- [x] 4.5 Verify `ProcessorFactory` resolves all supported Docker-mounted file formats.

## 5. Dependency and Image Hygiene

- [x] 5.1 Add `.dockerignore` coverage for virtual environments, node modules, caches, secrets, and generated build output.
- [x] 5.2 Decide and document whether the Docker dependency set is CPU-only by default.
- [x] 5.3 Ensure generated ChromaDB and model cache data are not baked into Docker images.

## 6. Documentation and Verification

- [x] 6.1 Document Docker environment setup and required variables in README or deployment docs.
- [x] 6.2 Document how to build images and start services with Docker Compose.
- [x] 6.3 Document how to run the indexing job before first chat usage.
- [x] 6.4 Document how to stop services and clean generated Docker volumes.
- [x] 6.5 Verify backend `/health` through Compose.
- [x] 6.6 Verify frontend chat submission reaches `POST /chat` through Compose.
- [x] 6.7 Verify a missing-index or missing-secret failure returns a descriptive error.
