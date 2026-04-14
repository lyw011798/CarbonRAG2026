## ADDED Requirements

### Requirement: Hash-based Incremental Extraction
The system SHALL compute a SHA256 hash for each raw file and persist this hash mapping. On subsequent runs, if a file's hash matches the stored hash, the system SHALL skip the `extract` and `clean` stages for that file.

#### Scenario: Unchanged file skipped
- **WHEN** the system is invoked for a file whose hash is already stored and matches
- **THEN** it skips the `extract` and `clean` stages for that file and uses the existing processed file (`data/processed/*.txt`).

#### Scenario: Modified file processed
- **WHEN** the system is invoked for a file whose hash has changed
- **THEN** it performs the `extract` and `clean` stages and updates the stored hash.

### Requirement: Rebuild Pipeline
The system SHALL support wiping the processed data and cache to force a fresh pipeline run.

#### Scenario: Rebuilding pipeline state
- **WHEN** a rebuild is requested
- **THEN** all `.txt` files in `data/processed/` and the `.hashes.json` cache are deleted before the pipeline executes.

### Requirement: Idempotent Vector Storage
The system SHALL verify whether a chunk ID already exists in the vector store before attempting to embed and insert it.

#### Scenario: Chunk already embedded
- **WHEN** the system attempts to store a chunk that is already present in ChromaDB
- **THEN** the store skips the embedding and insertion of that specific chunk.
