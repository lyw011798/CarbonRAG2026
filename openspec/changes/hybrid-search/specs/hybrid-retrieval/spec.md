## ADDED Requirements

### Requirement: BM25 Local Indexing
The system SHALL ingest tokenized chunk text into a BM25 local index alongside normal Vector storage, and persist this state locally to the DB path.

#### Scenario: Ingestion pipeline run
- **WHEN** chunks are added to `VectorStore` via `add_documents`
- **THEN** the system updates the BM25 model and saves it a pickle file alongside the Chroma database

### Requirement: Reciprocal Rank Fusion Retrieval
The system SHALL merge pure semantic search and purely sparse (BM25) search scores using Reciprocal Rank Fusion algorithmic logic during query execution.

#### Scenario: User queries explicit data point
- **WHEN** a user queries for an exact table value (like "300")
- **THEN** the system retrieves highly ranked chunks from BM25 and Chroma, applying RRF scoring to ensure exact match relevance overtakes fuzzy string similarity.
