## 1. Foundation & Base Processors

- [x] 1.1 Create `DocumentProcessor` ABC in `src/processors/base.py` defining the interface for document ingestion.
- [x] 1.2 Create `ProcessorFactory` in `src/processors/factory.py` to resolve processors by file extension.

## 2. Format Specific Processors

- [x] 2.1 Implement `PDFProcessor` in `src/processors/pdf.py` utilizing `pdfplumber` for table extraction and `pymupdf` fallback.
- [x] 2.2 Implement `TextProcessor` in `src/processors/text.py` including strict `UTF-8` and legacy `BIG5` encoding detection.
- [x] 2.3 Implement `MarkdownProcessor` in `src/processors/markdown.py` to strip syntax while preserving `# Heading` hierarchy.
- [x] 2.4 Implement `HTMLProcessor` in `src/processors/html.py` using `beautifulsoup4` to selectively extract body text and remove noise.

## 3. Chunking & Storage Components

- [x] 3.1 Implement `ChunkStrategy` in `src/chunker.py` to structure chunks along "第X條" boundaries and append metadata.
- [x] 3.2 Implement `VectorStore` in `src/store.py` encapsulating ChromaDB and initializing local `sentence-transformers`.
- [x] 3.3 Create `data_update.py` CLI function to orchestrate the directory traversal and ingestion pipeline using the built core classes.

## 4. Query Engineering

- [x] 4.1 Implement `RAGQuery` in `src/query.py` utilizing `LiteLLM` and injecting the Taiwan regulatory context prompt.
- [x] 4.2 Create `rag_query.py` CLI function managing interactive query loops, and attaching file and page citations to answers.

## 5. Domain Skill Generative Assembly

- [x] 5.1 Implement `SkillBuilder` in `src/builder.py` containing predefined query groups spanning core domain concepts and entities.
- [x] 5.2 Create `skill_builder.py` CLI function coordinating RAG evaluation calls to assemble and write out the final `skill.md` reference text.
