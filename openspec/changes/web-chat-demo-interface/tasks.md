## 1. Frontend Setup

- [x] 1.1 Create an isolated React + TypeScript frontend app directory with Vite-compatible project structure.
- [x] 1.2 Add Tailwind configuration and global styles for the chat demo shell.
- [x] 1.3 Add npm scripts for local development, build, and type checking.

## 2. Chat Contract and API Client

- [x] 2.1 Define strong TypeScript types for chat roles, messages, request payloads, responses, and API errors.
- [x] 2.2 Implement a `sendChatMessage` API function that posts visible conversation messages to `POST /chat`.
- [x] 2.3 Add explicit handling for network failures, non-2xx responses, and malformed response bodies.

## 3. Chat State Management

- [x] 3.1 Implement a `useChat` hook that owns message history, pending state, error state, and submit behavior.
- [x] 3.2 Ensure empty or whitespace-only messages are rejected before creating API requests.
- [x] 3.3 Ensure user messages append immediately and assistant messages append only after successful API responses.
- [x] 3.4 Ensure failed requests preserve existing message history and expose a descriptive error.

## 4. Chat UI Components

- [x] 4.1 Implement `ChatApp` to compose the full-page chat layout.
- [x] 4.2 Implement `ChatHeader` with concise demo context and polished visual hierarchy.
- [x] 4.3 Implement `MessageList` with chronological message rendering and an empty state.
- [x] 4.4 Implement `MessageBubble` with distinct user and assistant styling.
- [x] 4.5 Implement `ChatInput` with textarea input, submit button, disabled state, and keyboard submit behavior.
- [x] 4.6 Implement `ErrorBanner` for visible descriptive request failures.

## 5. UX Polish

- [x] 5.1 Add an assistant loading indicator while `POST /chat` is pending.
- [x] 5.2 Add auto-scroll behavior for new messages, loading state, and visible errors.
- [x] 5.3 Tune Tailwind spacing, colors, borders, and responsive behavior for a minimal polished desktop and mobile experience.
- [x] 5.4 Keep existing `.pdf`, `.txt`, `.md`, and `.html` ingestion code paths unchanged while adding the frontend demo.

## 6. Verification

- [x] 6.1 Run the frontend type check and build commands.
- [ ] 6.2 Manually verify successful chat submission against `POST /chat`.
- [ ] 6.3 Manually verify loading, error, malformed response, empty input, message history, and auto-scroll behavior.
