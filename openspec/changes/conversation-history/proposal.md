## Why

The current web chat demo only displays the active session's conversation history. Users cannot easily review past discussions, manage multiple conversation threads, or maintain a persistent record across browser sessions. Adding conversation history enables users to organize, search, and resume previous chats, improving the overall demo experience and making it more practical for exploring the Taiwan carbon knowledge base across multiple queries.

## What Changes

- Add a left sidebar displaying all saved conversations with search, delete, and rename capabilities
- Persist conversations to browser localStorage so users can resume conversations across browser sessions
- Auto-create a new blank conversation when the app loads
- Allow users to continue chatting in previously saved conversations by clicking them in the sidebar
- Implement conversation title management (auto-naming, user rename)
- Support searching and filtering conversations by title

## Capabilities

### New Capabilities

- `conversation-history`: Covers localStorage-backed conversation storage, retrieval, listing, searching by title, and deletion of entire conversations
- `conversation-sidebar`: Covers the left sidebar UI component that displays the conversation list, search box, rename/delete actions, and "New Chat" button
- `conversation-context-switching`: Covers the ability to click a conversation in the sidebar and restore its message history to the main chat area, allowing users to continue the conversation or view past messages

### Modified Capabilities

- `web-chat-demo`: The main chat interface now supports multi-conversation workflow instead of single-session-only workflow

## Impact

- **Frontend**: New React components (`ConversationSidebar`, `ConversationList`, `ConversationItem`), new custom hook (`useConversationHistory`), updated `ChatApp` layout to include sidebar
- **State Management**: Extend `use-chat` hook to manage active conversation context; new localStorage manager for persistence
- **No Backend Changes**: All persistence is client-side; backend `/chat` endpoint behavior unchanged
- **Styling**: Add sidebar styling with Tailwind, integrate with existing dark gradient theme

## Non-goals

- User authentication or per-user conversation partitioning
- Cloud/backend synchronization of conversation history
- Exporting conversations or generating shareable links
- Advanced conversation metadata (tags, categories, attachments)
- Full-text search of message content (search by title only)
