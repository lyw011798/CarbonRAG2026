## Context

The current project has a Python RAG stack (`data_update.py`, `rag_query.py`, `src/query.py`, `src/store.py`) and a Vite React frontend under `frontend/`. The frontend expects a `POST /chat` API, while the Python code owns ingestion, ChromaDB persistence, hybrid retrieval, and LLM calls. Local setup is sensitive to Python version, platform-specific packages, Node dependencies, and whether `db/chroma` has already been built.

Docker deployment should make local startup repeatable without changing the existing RAG behavior. The design must preserve the current ingestion paths for `.pdf`, `.txt`, `.md`, and `.html`, where `ProcessorFactory` selects the processor and each processor owns extraction for its format.

## Goals / Non-Goals

**Goals:**

- Provide a Docker Compose deployment that starts the chat frontend and RAG backend with one command.
- Provide a background-capable job path for rebuilding or refreshing the ChromaDB index.
- Persist ChromaDB data, BM25 cache, raw documents, processed text, and model caches across container restarts.
- Keep environment variables such as `GEMINI_API_KEY`, `LITELLM_API_KEY`, `LITELLM_BASE_URL`, `CHROMA_PERSIST_DIR`, and model settings outside the image.
- Use the existing ownership model: `data_update.py` owns ingestion orchestration, `ProcessorFactory` owns `.pdf`/`.txt`/`.md`/`.html` routing, `VectorStore` owns retrieval storage, and `RAGQuery` owns answer generation.

**Non-Goals:**

- Replace the Python CLI commands or remove local non-Docker development support.
- Change chunking, retrieval, embedding, prompt, citation, or supported document-format behavior.
- Add Kubernetes, managed cloud services, Terraform, CI/CD, or production secret-management infrastructure.
- Bundle API keys or generated vector database artifacts into the container image.

## Decisions

### Use Docker Compose as the deployment boundary

Docker Compose will define the local deployment because the project has multiple cooperating runtimes: Python backend, React frontend, persistent data volumes, and one-off indexing jobs.

Alternative considered: a single all-in-one image serving both API and static frontend. This is simpler to run but couples frontend build/runtime concerns to the Python image and makes future backend/frontend scaling harder.

### Build a dedicated Python backend image

The backend image will install Python dependencies and run the HTTP chat backend. The container will mount or receive volumes for `data/raw`, `data/processed`, `db/chroma`, and model caches. Runtime configuration will come from `.env`.

Alternative considered: run the existing CLI directly as the backend. This does not satisfy the frontend `POST /chat` contract and would not provide a long-running HTTP service.

### Keep indexing as a repeatable background job

Index creation and refresh should run as a Compose service profile or documented command that executes `python data_update.py --rebuild` or equivalent. This keeps expensive ingestion and embedding work separate from API startup while allowing operators to rebuild the vector database before or after starting services.

Alternative considered: rebuild the index automatically on backend container startup. This makes startup slow, can surprise users by mutating persistent data, and creates failure modes unrelated to serving chat requests.

### Serve the frontend as a static production build

The frontend image should build the Vite app and serve static assets through a lightweight HTTP server. API routing should target the backend service by Compose service name or by a configurable `VITE_CHAT_API_BASE_URL`.

Alternative considered: run `npm run dev` in Docker. This is useful for development but should not be the default deployment path because it depends on dev tooling and hot reload behavior.

### Persist generated state through named volumes or bind mounts

ChromaDB data, BM25 cache, processed text, and model downloads must survive container replacement. Compose should make those paths explicit so operators understand what data is generated and what can be backed up or deleted.

Alternative considered: store generated artifacts inside the image. This would make rebuilds large, leak environment-specific state, and require rebuilding images whenever source documents change.

## Risks / Trade-offs

- Python dependency lock contains platform-specific GPU packages → Provide a Docker image based on a Linux Python version supported by the project and document CPU/GPU dependency expectations.
- First index build can be slow because embedding models and documents must be processed → Keep indexing explicit and persist model/vector caches.
- Missing API keys cause runtime chat failures → Validate environment variables during backend startup or return descriptive health/chat errors.
- Large model caches and ChromaDB data can consume disk space → Document volume paths and cleanup commands.
- Frontend/backend URL mismatch can break `POST /chat` → Define a single documented Compose network route and keep frontend API base URL configurable.

## Migration Plan

1. Add Docker backend, frontend, and Compose configuration.
2. Add `.dockerignore` files to keep local virtual environments, node modules, caches, secrets, and generated artifacts out of image builds.
3. Document environment setup from `.env.example`.
4. Run the indexing service once to create or refresh `db/chroma`.
5. Start backend and frontend services through Compose.
6. Verify `/health`, `POST /chat`, and frontend chat submission.
7. Roll back by stopping Compose services and continuing to use existing local CLI/frontend commands.

## Open Questions

- Should the default Docker dependency set be CPU-only for Windows/Linux portability, with optional GPU instructions documented separately?
- Should the production frontend route `/chat` through the static web server proxy, or should the browser call the backend service through a public API URL?
- Should the backend expose source citations in the initial Docker deployment response contract, or preserve the current frontend contract of only returning an assistant message?
