## 1. CLI Entry Point

- [x] 1.1 Update `rag_query.py` argument parsing to support both default interactive mode and optional `--query`, `--top-k`, and `--model` flags.
- [x] 1.2 Add a one-time execution path in `rag_query.py` that loads `.env`, initializes `VectorStore` and `RAGQuery`, runs a single query, and exits.
- [x] 1.3 Keep the existing interactive loop as the default branch when `--query` is not provided.

## 2. Query Orchestration

- [x] 2.1 Update `src/query.py::RAGQuery.query` to accept the one-shot query flow inputs and return structured answer-plus-source data for CLI formatting.
- [x] 2.2 Adjust `src/query.py::RAGQuery` prompt assembly so the model is instructed to answer in the same language as the question and cite retrieved sources with `[1][2]` notation.
- [x] 2.3 Preserve the separation of concerns so retrieval still comes from `VectorStore` and LiteLLM invocation remains inside `RAGQuery`.

## 3. Source Formatting

- [x] 3.1 Update source metadata handling so the CLI can print numbered source lines with filename, section, and score information.
- [x] 3.2 Ensure the one-time query path formats stdout as an `Answer:` block followed by a `Sources:` block.

## 4. Verification

- [x] 4.1 Add or update tests for default interactive-mode behavior and the new `--query` one-time mode.
- [x] 4.2 Add or update tests for output formatting and source numbering so the CLI response shape is stable.