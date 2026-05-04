## Context

The web chat demo currently stores conversation state only in React component memory. Switching between browser tabs or refreshing the page loses all conversation context. Users cannot organize multiple discussions or refer back to previous queries. This limits the usefulness of the demo for exploring the Taiwan carbon knowledge base across multiple sessions.

## Goals / Non-Goals

**Goals:**
- Enable persistent multi-conversation support using browser localStorage
- Provide an intuitive sidebar UI for conversation management (list, search, delete, rename)
- Allow users to switch between conversations and continue chatting in previous threads
- Auto-create a new conversation on app startup
- Maintain compatibility with existing `/chat` backend endpoint

**Non-Goals:**
- Server-side persistence or user authentication
- Full-text search of message content (title-only search)
- Advanced conversation features (tagging, archiving, export)
- Changes to backend RAG query logic or `/chat` endpoint behavior

## Decisions

### 1. Client-side localStorage for Persistence
**Decision**: Store all conversations in browser localStorage, not backend.
**Rationale**: Keeps backend stateless (no new database tables or API changes). Matches the demo scope (single-user, session-based). Simpler implementation with instant UI responsiveness.
**Alternatives Considered**: Backend storage would require auth, user isolation, API changes, and database schema. Not justified for a demo.
**Trade-off**: Conversation data lost if browser cache is cleared; not synced across tabs/devices.

### 2. Conversation Data Model
**Decision**: Each conversation is `{ id: string, title: string, messages: ChatMessage[], createdAt: ISO, updatedAt: ISO }`. Store in localStorage as `conversations: Conversation[]`.
**Rationale**: Minimal structure, easy to serialize/deserialize, room to extend. `id` enables stable references; `createdAt/updatedAt` support sorting and UI hints.
**Trade-off**: No compression; large conversation sets will increase localStorage footprint. Typical browser limit is 5-10MB, sufficient for demo use.

### 3. Auto-create on Load
**Decision**: Every app load creates a new blank conversation. Past conversations remain in sidebar.
**Rationale**: Provides a clean slate for new queries; users can click sidebar to resume old conversations. Matches ChatGPT UX.
**Alternatives Considered**: Remember "last active" conversation. Adds state complexity; simpler to always start fresh.

### 4. Context Switching via Sidebar Click
**Decision**: Clicking a conversation in sidebar swaps the active conversation ID, loads its messages, and allows continuation in the chat input.
**Rationale**: Users can review old messages and append new ones. Simple state transition: `activeConversationId` changes, UI re-renders with different message history.
**Trade-off**: No explicit "view-only" mode; if user types in an old conversation, they extend it. Feature, not bug.

### 5. Component & Hook Architecture
**Decision**: 
- New `useConversationHistory()` hook manages all conversation CRUD, localStorage sync, and active conversation state
- New `<ConversationSidebar />` component displays list, search box, delete/rename buttons
- Refactor `<ChatApp />` to include sidebar and wire up context switching
- Update `use-chat` hook to accept optional `conversationId` parameter (or derive from sidebar state)

**Rationale**: Separates concerns—`useConversationHistory` owns persistence logic, `<ConversationSidebar />` owns UI, `use-chat` remains focused on query/response flow.
**Alternatives Considered**: Store conversations inside `use-chat`. Couples persistence to chat logic; harder to test separately.

### 6. Search Implementation
**Decision**: Client-side string matching on conversation titles. Real-time filtering as user types.
**Rationale**: Fast, no backend call, works offline. Title-only scope (as per proposal) keeps logic simple.
**Trade-off**: Cannot search message content; acceptable per proposal non-goals.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **localStorage quota exceeded** (5-10MB typical) | Warn user when approaching limit; provide UI to delete old conversations. Not expected in demo use. |
| **Data loss on cache clear** | Document in README that conversations are browser-local. Acceptable for demo; production would need export/sync. |
| **No cross-tab sync** | Each tab has independent conversation state. Acceptable; users expect this behavior. |
| **Title collision** | UUIDs ensure ID uniqueness; title duplicates are allowed (UI shows creation date for disambiguation). |
| **Performance with large history** | localStorage read on app boot scales O(n). With 100+ conversations, noticeable delay. Mitigation: pagination or lazy-load in sidebar (future work). |

## Migration Plan

**Rollout**: No backend changes, pure frontend feature.

1. **Develop & test** new components and hooks locally
2. **Merge** to main; ship with next frontend deployment (no backend coordination needed)
3. **Rollback**: Remove sidebar component, clear localStorage key on user's browser (no server-side cleanup)

## Open Questions

1. Should conversation titles default to "New Chat" or first few words of first message? → Recommend: "New Chat", allow immediate rename
2. Should deleted conversations be recoverable (soft delete with archive view)? → Recommend: Hard delete for demo simplicity; future work can add undo
