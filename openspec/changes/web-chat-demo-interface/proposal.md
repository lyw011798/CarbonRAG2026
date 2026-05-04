## Why

The current RAG system is primarily usable through Python CLI entrypoints, which is useful for development but not ideal for demonstrating the assistant experience to non-technical users. A minimal polished web chat demo will make the Taiwan carbon market knowledge base easier to evaluate, share, and iterate on before committing to a production product surface.

## What Changes

- Add a React + Tailwind frontend demo that presents a ChatGPT-like conversation interface.
- Add message history in the browser session so users can review the current conversation while asking follow-up questions.
- Integrate the frontend with a `POST /chat` API endpoint that accepts user messages and returns assistant responses.
- Show clear loading and error states for chat requests, including descriptive failure messages.
- Automatically scroll to the newest message after user, assistant, loading, or error updates.
- Use maintainable frontend structure with small typed components and focused state management.
- Preserve the existing ingestion and retrieval model: `.pdf`, `.txt`, `.md`, and `.html` source documents continue to be processed by the current Python pipeline and are not changed by this demo.

## Capabilities

### New Capabilities

- `web-chat-demo`: Covers the React + Tailwind chat frontend demo, including message rendering, local conversation history, `POST /chat` integration, loading and error UX, auto scroll, and polished responsive layout.

### Modified Capabilities

- None

## Non-goals

- Building a production authentication, account, or persistent chat history system.
- Replacing the existing Python CLI query workflows.
- Changing ingestion, chunking, vector storage, embeddings, or source document processing for `.pdf`, `.txt`, `.md`, or `.html` files.
- Implementing streaming responses, tool calls, multimodal input, or admin configuration screens.
- Defining the server implementation of `POST /chat` beyond the request and response contract needed by the frontend demo.

## Impact

- Adds a frontend application surface, expected to live outside the existing Python `src/` RAG modules so the backend pipeline remains isolated.
- Introduces React, Tailwind, TypeScript, and frontend build tooling dependencies.
- The chat app owns presentational UI components, browser-session message state, request lifecycle handling, and auto-scroll behavior.
- The API client module owns the `POST /chat` request/response contract and explicit error normalization.
- Existing Python classes keep their responsibilities: `RAGQuery` owns retrieval and generation, `VectorStore` owns ChromaDB lookup and embeddings, and `DocumentProcessor` subclasses continue to own `.pdf`, `.txt`, `.md`, and `.html` extraction.
