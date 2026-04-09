## ADDED Requirements

### Requirement: Document ingestion and structural chunking
The system SHALL ingest raw policy documents (PDF, Markdown) and chunk them according to structural boundaries (e.g., articles like `第X條`) rather than fixed character counts. Include valid_date and jurisdiction metadata per chunk.

#### Scenario: Ingesting a regulatory document
- **WHEN** the user runs `data_update.py` with a new regulation document
- **THEN** the chunker splits the text by article boundaries and attaches appropriate metadata (source, jurisdiction, valid_date)

### Requirement: Table normalization
The system SHALL convert structured table data (such as carbon fee rates) into normalized natural language text sentences prior to embedding.

#### Scenario: Processing a carbon fee schedule table
- **WHEN** a PDF containing carbon fee rates is ingested
- **THEN** the table is normalized into sentences like "The general carbon fee rate for Taiwan in 2025 is $300 NTD per ton." before indexing

### Requirement: Incremental update and full rebuild
The system SHALL support incremental updates using file hash comparison by default, and a full wipe and reindex when the `--rebuild` flag is provided.

#### Scenario: Running an incremental update
- **WHEN** the user runs `data_update.py` and only one document has changed hash
- **THEN** only the changed document is re-embedded and upserted to the vector database

#### Scenario: Triggering a complete rebuild
- **WHEN** the user runs `data_update.py --rebuild`
- **THEN** the existing vector index is wiped completely and rebuilt from all current source files
