## Context

The project currently exposes RAG interactions through Python CLI entrypoints and backend modules such as `RAGQuery` and `VectorStore`. The new demo adds a browser-based chat surface without changing the existing document ingestion path for `.pdf`, `.txt`, `.md`, or `.html` files.

The frontend should be small enough to understand quickly, but structured enough that future work can add streaming, source cards, or persistent history without rewriting the demo. The backend contract is intentionally narrow: the browser sends chat messages to `POST /chat` and renders the returned assistant message.

## Goals / Non-Goals

**Goals:**

- Build a React + Tailwind single-page chat demo with a polished ChatGPT-like layout.
- Keep code maintainable by separating typed data models, API calls, chat state, and presentational components.
- Provide browser-session message history, loading state, explicit error handling, and auto-scroll behavior.
- Define a stable `POST /chat` frontend contract that can be backed by the existing RAG pipeline later.
- Preserve current ownership in the Python system: `RAGQuery` owns retrieval and generation, `VectorStore` owns ChromaDB lookup, and document processors continue to own `.pdf`, `.txt`, `.md`, and `.html` extraction.

**Non-Goals:**

- No authentication, accounts, or persisted conversation storage.
- No streaming token output.
- No document upload or ingestion changes.
- No replacement of `rag_query.py` or other CLI entrypoints.
- No backend implementation details beyond the frontend request and response contract.

## Decisions

### Use a Separate React + Tailwind Frontend App

Create the chat demo as a dedicated frontend app, expected under a directory such as `frontend/`, using React, TypeScript, and Tailwind.

Rationale: the current repository is a Python RAG project with no existing JavaScript package. A separate frontend boundary avoids mixing build systems into the Python `src/` package and makes the demo easy to run, test, and remove if needed.

Alternatives considered:

- Add static HTML directly to the Python project: simpler tooling, but harder to keep maintainable as UI state grows.
- Use a larger framework such as Next.js: useful for production routing and server features, but unnecessary for a minimal demo that only needs a single chat page.

### Keep Chat State in a Typed Hook

Implement a hook such as `useChat` to own the message list, pending state, request submission, error state, and retry-safe cleanup.

Rationale: chat state has request lifecycle complexity. Keeping it in one hook keeps UI components mostly presentational while making loading and error handling explicit.

Alternatives considered:

- Keep all state directly in `App`: acceptable for a prototype, but it will become noisy once request normalization and auto-scroll are added.
- Add a global state library: unnecessary for one page and one conversation.

### Use a Small API Client for `POST /chat`

Create an API client module such as `chat-api.ts` that exposes a typed `sendChatMessage` function.

Expected request:

```json
{
  "messages": [
    { "role": "user", "content": "..." }
  ]
}
```

Expected response:

```json
{
  "message": { "role": "assistant", "content": "..." }
}
```

The client should validate HTTP failures, malformed responses, and network failures, then return descriptive errors for the UI.

Rationale: the API boundary is the most likely integration point to change. A dedicated client avoids scattering fetch behavior across components.

Alternatives considered:

- Call `fetch` directly from the input handler: faster initially, but makes error handling and tests harder.
- Mirror the full backend RAG response shape immediately: premature until the server contract is available.

### Compose the UI from Focused Components

Use components with clear responsibilities:

- `ChatApp` owns page composition.
- `ChatHeader` owns title and short demo context.
- `MessageList` owns scrollable message rendering and empty state.
- `MessageBubble` owns user/assistant visual treatment.
- `ChatInput` owns the textarea, submit affordance, disabled state, and keyboard behavior.
- `ErrorBanner` owns visible error feedback.

Rationale: this keeps each file small and makes it easier to adjust styling without touching request logic.

### Preserve Existing RAG Processing Boundaries

The frontend does not change the existing processing hierarchy:

```text
DocumentProcessor
├── PDFProcessor       (.pdf: table-aware extraction and page cleanup)
├── TextProcessor      (.txt: encoding detection for UTF-8 / BIG5)
├── MarkdownProcessor  (.md: markdown cleanup while preserving headings)
└── HTMLProcessor      (.html: removes nav/footer/script/style noise)

ProcessorFactory resolves processor by file extension.
RAGQuery owns retrieval, prompt assembly, and model invocation.
VectorStore owns embeddings and ChromaDB retrieval.
```

Rationale: the demo is a presentation layer. Keeping ingestion and retrieval unchanged limits regression risk.

## Risks / Trade-offs

- `POST /chat` backend shape may differ from the frontend assumption → Keep all request and response handling inside the API client so the contract can be adjusted in one place.
- Frontend dependencies add a second toolchain → Keep the app isolated and document simple npm scripts.
- Chat history is browser-session only → Make this explicit in UI behavior and avoid implying persistence.
- Non-streaming responses can feel slower than modern chat apps → Use a clear loading indicator and disabled submit state while preserving the option to add streaming later.
- Tailwind styling can become inconsistent if classes sprawl → Keep repeated layout patterns inside focused components rather than duplicating large class lists.

## Migration Plan

1. Add the frontend app and install React, TypeScript, Tailwind, and build tooling.
2. Implement typed chat models, API client, chat state hook, and presentational components.
3. Wire the app to `POST /chat` through a configurable base URL or same-origin path.
4. Verify the frontend handles successful responses, loading state, explicit errors, empty input, and auto-scroll.
5. Rollback by removing the isolated frontend directory and associated package files if the demo is not needed.

## Open Questions

- Should `POST /chat` accept only the current user message or the full visible message history?
- Should the frontend eventually render citations returned by the RAG backend?
- Should the demo run as same-origin with a backend proxy during local development, or use a configurable API base URL?
