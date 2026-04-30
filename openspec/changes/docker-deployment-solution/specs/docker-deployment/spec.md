## ADDED Requirements

### Requirement: Compose Deployment
The system MUST provide a Docker Compose deployment that can start the RAG backend and frontend interface as separate services.

#### Scenario: Start deployment services
- **WHEN** an operator starts the Docker Compose deployment with the documented command
- **THEN** the system starts a backend service for chat API requests and a frontend service for the web interface

#### Scenario: Services communicate inside Compose
- **WHEN** the frontend sends a chat request through the configured deployment route
- **THEN** the request reaches the backend service without requiring host-specific hardcoded container addresses

### Requirement: Backend Container Runtime
The system MUST provide a backend container runtime for the Python RAG service that uses the existing query and storage components.

#### Scenario: Backend starts with valid configuration
- **WHEN** the backend container starts with required environment variables and available dependencies
- **THEN** it exposes a health endpoint and a `POST /chat` endpoint backed by `RAGQuery` and `VectorStore`

#### Scenario: Backend configuration is incomplete
- **WHEN** the backend container starts or receives a chat request without required runtime configuration
- **THEN** it returns a descriptive error instead of failing silently

### Requirement: Frontend Container Runtime
The system MUST provide a frontend container runtime that builds and serves the React chat interface.

#### Scenario: Frontend container is started
- **WHEN** the frontend container starts from the deployment image
- **THEN** it serves the production-built chat interface over HTTP

#### Scenario: User submits chat from frontend
- **WHEN** a user submits a non-empty message in the deployed frontend
- **THEN** the frontend sends the request to the deployed backend chat endpoint and renders the assistant response returned by the backend

### Requirement: Background Indexing Job
The system MUST provide a documented Docker-run path for rebuilding or refreshing the RAG index separately from the long-running backend and frontend services.

#### Scenario: Operator rebuilds the index
- **WHEN** an operator runs the documented indexing job
- **THEN** the system executes the existing ingestion pipeline and writes generated vector data to the configured ChromaDB persistence path

#### Scenario: Indexing preserves supported formats
- **WHEN** the indexing job processes source documents
- **THEN** it continues to support `.pdf`, `.txt`, `.md`, and `.html` inputs through the existing processor ownership model

### Requirement: Persistent Data and Caches
The system MUST persist generated RAG data and model caches across container restarts.

#### Scenario: Containers are recreated
- **WHEN** the backend or indexing container is recreated after a successful index build
- **THEN** the ChromaDB data, BM25 cache, processed text, raw documents, and model caches remain available through documented volumes or bind mounts

#### Scenario: Operator inspects storage
- **WHEN** an operator reviews the deployment documentation
- **THEN** the documentation identifies which mounted paths contain persistent data and which can be safely regenerated

### Requirement: Environment Configuration
The system MUST keep runtime configuration and secrets outside container images.

#### Scenario: API credentials are configured
- **WHEN** an operator provides credentials through the documented environment mechanism
- **THEN** the backend uses those values at runtime without baking them into Docker images

#### Scenario: Deployment example is reviewed
- **WHEN** an operator reviews the Compose and environment examples
- **THEN** the examples include the variables needed for model selection, LiteLLM or Gemini credentials, ChromaDB persistence, and service ports

### Requirement: Deployment Documentation
The system MUST document how to build, start, verify, rebuild data, and stop the Docker deployment.

#### Scenario: Operator follows setup docs
- **WHEN** an operator follows the Docker deployment instructions from a clean checkout
- **THEN** they can build images, create or refresh the index, start services, open the frontend, and verify backend health

#### Scenario: Deployment verification fails
- **WHEN** a documented verification step fails
- **THEN** the documentation provides enough context to identify missing dependencies, missing environment variables, missing index data, or service startup failures
