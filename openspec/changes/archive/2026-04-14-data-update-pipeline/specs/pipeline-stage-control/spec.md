## ADDED Requirements

### Requirement: Pipeline Stage Selection
The system SHALL support executing one or more data processing stages explicitly, skipping the others. The defined stages are `extract`, `clean`, `chunk`, `embed`, and `store`.

#### Scenario: Running selected stages only
- **WHEN** the system is invoked to run only the `extract` and `clean` stages
- **THEN** it executes the extraction and cleaning logic but skips chunking, embedding, and storing.

#### Scenario: Running stages requiring existing parsed data
- **WHEN** the system is invoked to run only `embed` and `store`
- **THEN** the system uses the already processed `.txt` files in `data/processed/` to generate chunks, embeddings, and save to the vector store.
