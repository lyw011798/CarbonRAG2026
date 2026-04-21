# chunk-optimization Specification

## Purpose
TBD - created by archiving change optimize-chunking. Update Purpose after archive.
## Requirements
### Requirement: Stricter Legal Strategy Detection
The `ChunkStrategy` SHALL require a minimum of 3 matches of the "第X條" pattern before classifying a document's strategy as 'legal'.

#### Scenario: Document with sporadic legal citations
- **WHEN** a document has fewer than 3 lines starting with a legal article code (e.g., "第二十八條")
- **THEN** the chunker SHALL NOT select the 'legal' strategy, falling back to other strategies like numbered sections or fallback.

### Requirement: Conservative Sub-Chunk Limit
The `ChunkStrategy` SHALL limit `max_chunk_size` to 250 characters and increase `overlap_lines` to 2 in order to fit within the `paraphrase-multilingual-MiniLM-L12-v2` sequence length limit without silent truncation.

#### Scenario: Large fallback paragraph chunking
- **WHEN** a document is sub-chunked via `_basic_sub_chunk`
- **THEN** no individual chunk SHALL exceed 250 characters + header injection size, ensuring all contents, including trailing tables, are discretely chunked and deeply embedded.

