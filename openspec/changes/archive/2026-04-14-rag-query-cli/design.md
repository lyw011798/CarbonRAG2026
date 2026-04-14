## Context

`rag_query.py` currently provides a terminal-driven interactive loop on top of `src/query.py::RAGQuery` and `src/store.py::VectorStore`. The codebase already separates retrieval, embedding, and LLM invocation, so this change should preserve those boundaries while extending the CLI with a one-time query mode.

The existing implementation already loads `.env`, initializes the local ChromaDB-backed vector store, and supports LiteLLM-based answering. The new behavior must keep the interactive loop as the default entrypoint and add a non-interactive query path for scripts and shell usage.

## Goals / Non-Goals

**Goals:**
- Keep the current interactive multi-turn CLI available when `rag_query.py` is run without arguments.
- Add a one-time query mode driven by `--query` that runs a single retrieval and generation cycle, then exits.
- Support `--top-k` and `--model` flags for both interactive and one-time modes.
- Preserve the existing RAG responsibilities: `VectorStore` handles embedding and ChromaDB search; `RAGQuery` handles prompt construction and LiteLLM calls.
- Print answers and citations in a stable stdout format that is easy to read and script against.

**Non-Goals:**
- Replacing the interactive loop.
- Adding streaming or chat history persistence.
- Changing the ingestion pipeline, chunking strategy, or source document support.
- Redesigning the vector database or embedding model.

## Decisions

### CLI Mode Selection

`rag_query.py` will branch on whether `--query` is provided:
- No `--query`: enter the existing interactive loop.
- With `--query`: execute a single query, print the answer and sources, and exit.

This preserves backward compatibility for existing terminal users while making automation straightforward.

### Query Parameters

The CLI will expose:
- `--query`: required for one-time mode; the question string.
- `--top-k`: retrieval depth, defaulting to 5.
- `--model`: LiteLLM model identifier, defaulting to `gemini-2.5-flash`.

The one-time path should pass these values directly into the query layer rather than duplicating retrieval or prompt logic in the CLI.

### Prompt Assembly and Language Policy

`src/query.py::RAGQuery` should continue to build the model prompt from retrieved chunks. The prompt must instruct the model to:
- answer using the same language as the question,
- rely only on retrieved context,
- cite the retrieved sources with `[1][2]` style references.

This keeps prompt policy close to the generation boundary rather than in the CLI.

### Source Formatting

The query layer should return answer text plus structured source metadata. The CLI will format stdout as:

```text
Answer:
<LLM response>

Sources:
[1] <filename>  (section: <section>, score: <score>)
[2] <filename>  (section: <section>, score: <score>)
```

Keeping formatting in the CLI makes the output predictable without coupling the query layer to presentation concerns.

### Environment Loading

The CLI will load `.env` before instantiating the query stack so LiteLLM can read `LITELLM_API_KEY` and `LITELLM_BASE_URL` from the environment.

### Class Boundaries

`VectorStore` remains responsible for local embeddings and ChromaDB similarity search. `RAGQuery` remains responsible for:
- invoking the vector store,
- assembling the retrieval context,
- constructing the LiteLLM messages,
- calling LiteLLM,
- returning answer and source metadata.

`rag_query.py` remains a thin CLI wrapper that chooses mode and prints results.

## Architecture

```ascii
+-------------------+        +------------------+
| rag_query.py      | -----> | argparse mode    |
| CLI wrapper       |        | selection        |
+-------------------+        +------------------+
          |                             |
          | interactive loop            | one-time query
          v                             v
+-------------------+        +------------------+
| RAGQuery          | <----> | VectorStore      |
| prompt + LLM      |        | embeddings +     |
| orchestration     |        | ChromaDB search  |
+-------------------+        +------------------+
```

## Risks / Trade-offs

- Supporting two CLI modes increases branching in `rag_query.py`, but the logic stays small if the file remains a wrapper.
- Returning structured sources from the query layer may require small shape changes in downstream code, but it is necessary to produce stable citations.
- If the user provides a LiteLLM model name that differs from the project default format, the CLI should pass it through unchanged rather than trying to infer provider-specific aliases.