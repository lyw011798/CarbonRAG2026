## 1. Environment and Project Setup

- [ ] 1.1 Initialize a new Python project with empty `requirements.txt` and base directories.
- [ ] 1.2 Add dependencies: `sentence-transformers`, `chromadb`, `litellm`.
- [ ] 1.3 Create `/data/raw` placeholder for storing raw PDFs and policy files.

## 2. Ingestion Pipeline (`data_update.py`)

- [ ] 2.1 Implement document text extraction to read PDFs/Markdown.
- [ ] 2.2 Build structural text chunker to segment by articles (e.g., `第X條`).
- [ ] 2.3 Develop table normalizer to flatten tabular fee rates into descriptive sentences.
- [ ] 2.4 Attach source, valid_date, and jurisdiction metadata to generated chunks.
- [ ] 2.5 Initialize ChromaDB local client/collection and wire up local embedding generation.
- [ ] 2.6 Implement file hashing validation for incremental batch indexing.
- [ ] 2.7 Build CLI layer with `--rebuild` toggle to clear constraints and reload all.

## 3. Query Service (`rag_query.py`)

- [ ] 3.1 Setup vector similarity search to pull 5-10 context chunks for a query.
- [ ] 3.2 Build the LLM prompt wrapper to inject retrieved context and the strict "Taiwan regulatory perspective" instruction.
- [ ] 3.3 Configure `LiteLLM` to process formatted prompt, defaulting to `gemini-2.5-flash`.
- [ ] 3.4 Process output to aggressively append citations (source document and section) to the response output.

## 4. Skill Extraction (`skill_builder.py`)

- [ ] 4.1 Formulate topical sub-queries targeting "Core Concepts", "Entities", and "Current Status".
- [ ] 4.2 Query the RAG layer and merge returned summaries into a standard markdown tree.
- [ ] 4.3 Output final compilation sequentially to `skill.md`.

## 5. End-to-End Testing

- [ ] 5.1 Seed `/data/raw` with a sample regulation (e.g. Climate Change Response Act) and test run `data_update.py`.
- [ ] 5.2 Test retrieving accurate source chunks via `rag_query.py` on tricky concepts like CBAM vs TW rules.
- [ ] 5.3 Ensure `skill_builder.py` yields a well-formatted markdown file and verifies citations.
