## ADDED Requirements

### Requirement: Document parsing strategy
The system MUST implement a DocumentProcessor strategy to parse `.pdf`, `.txt`, `.md`, and `.html` formats utilizing a ProcessorFactory to resolve the correct subclass.

#### Scenario: Parse PDF document
- **WHEN** ingestion encounters a `.pdf` file
- **THEN** it resolves to PDFProcessor and extracts text and tables

#### Scenario: Parse HTML document
- **WHEN** ingestion encounters an `.html` file
- **THEN** it resolves to HTMLProcessor and strips navigation/script noise

#### Scenario: Parse Text document
- **WHEN** ingestion encounters a `.txt` file
- **THEN** it resolves to TextProcessor which utilizes encoding detection (UTF-8 / BIG5)

#### Scenario: Parse Markdown document
- **WHEN** ingestion encounters a `.md` file
- **THEN** it resolves to MarkdownProcessor and preserves the heading hierarchy

### Requirement: Legal structure chunking
The ChunkStrategy MUST chunk parsed texts sequentially at section or article boundaries (e.g. "第X條") to preserve context.

#### Scenario: Chunking a regulatory act
- **WHEN** a document string contains "第一條" and "第二條"
- **THEN** it creates separate chunks split at those article boundaries and prepends the article header to the chunk payload

### Requirement: Local Embedding and Vector Storage
The VectorStore MUST execute embedding calculations entirely locally utilizing `sentence-transformers` and commit vectors to the ChromaDB index.

#### Scenario: Saving embedded chunks
- **WHEN** chunking and embedding operations are complete
- **THEN** records are pushed into ChromaDB alongside required metadata fields: source, filename, page_num, valid_date, jurisdiction, carbon_type
