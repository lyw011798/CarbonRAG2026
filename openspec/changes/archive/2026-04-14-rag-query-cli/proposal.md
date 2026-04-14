## Why

The current `rag_query.py` entrypoint only supports an interactive loop, which works well for exploratory use but is awkward for scripts, shell pipelines, and one-off terminal lookups. A one-shot query mode is needed so users can ask one question, receive one answer, and exit cleanly without removing the existing interactive experience.

## What Changes

- Keep the current interactive loop in `rag_query.py` as the default behavior.
- Add an optional one-time CLI query flow driven by `--query` that runs a single retrieval and answer cycle, then exits.
- Add optional `--top-k` and `--model` flags so users can tune retrieval depth and LiteLLM model selection from the terminal in both modes where applicable.
- Keep retrieval and generation responsibilities in `src/query.py::RAGQuery`; keep ChromaDB access and embedding lookup in `src/store.py::VectorStore`.
- Read `GEMINI_API_KEY` and `GEMINI_BASE_URL` from `.env` before calling LiteLLM.
- Format stdout as an `Answer:` block followed by a `Sources:` block with numbered citations.
- Preserve the existing ingestion pipeline and its support for `.pdf`, `.txt`, `.md`, and `.html` source documents.

## Capabilities

### New Capabilities
- `rag-query`: adds a single-shot command-line query mode alongside the existing interactive multi-turn terminal loop, with explicit query arguments and source reporting.

### Modified Capabilities
- None

## Non-goals

- Replacing the interactive / multi-turn chat mode.
- Streaming output.
- Web interface.
- Changing the ingestion pipeline, chunking strategy, or supported source formats.

## Impact

- `rag_query.py` remains the interactive CLI entrypoint and also supports a one-time query mode for terminal use and automation.
- `src/query.py::RAGQuery` continues to own retrieval, prompt assembly, and LiteLLM invocation.
- `src/store.py::VectorStore` continues to own embedding and ChromaDB retrieval.
- The existing ingestion path still handles `.pdf`, `.txt`, `.md`, and `.html` documents, so this change only affects query-time behavior.
- The CLI output format is extended for the one-time mode, while the interactive prompt remains available for existing users.