## 1. Hook: useConversationHistory

- [x] 1.1 Create `frontend/src/hooks/useConversationHistory.ts` with conversation CRUD operations (create, delete, rename, getAll, setActive)
- [x] 1.2 Implement localStorage persistence (load on init, sync after each mutation)
- [x] 1.3 Add TypeScript types for Conversation (id, title, messages, createdAt, updatedAt)
- [x] 1.4 Implement auto-create new conversation on hook initialization

## 2. UI Components: Sidebar

- [x] 2.1 Create `frontend/src/components/conversation-sidebar.tsx` with search box, new chat button, and conversation list
- [x] 2.2 Create `frontend/src/components/conversation-item.tsx` for individual conversation display with delete/rename buttons
- [x] 2.3 Implement search filtering (case-insensitive title matching) in sidebar
- [x] 2.4 Implement delete confirmation dialog or inline deletion
- [x] 2.5 Implement inline rename mode (edit input on click, confirm/cancel actions)
- [x] 2.6 Add active conversation highlight styling (Tailwind)
- [x] 2.7 Style sidebar with dark theme matching existing chat area (responsive, scrollable list)

## 3. Integration: ChatApp Layout

- [x] 3.1 Refactor `frontend/src/components/chat-app.tsx` to include sidebar and main chat area side-by-side (flex layout)
- [x] 3.2 Wire up `useConversationHistory` hook in ChatApp
- [x] 3.3 Implement conversation context switching (click sidebar item → load messages → set active)
- [x] 3.4 Pass active conversation ID and message list to child components

## 4. Hook: use-chat Updates

- [x] 4.1 Update `frontend/src/hooks/use-chat.ts` to accept optional `conversationId` parameter
- [x] 4.2 Modify `submitMessage` to append messages to the active conversation (not just local state)
- [x] 4.3 Call `useConversationHistory.updateConversation` after each user/assistant message to sync localStorage
- [x] 4.4 Ensure full message history is sent to backend in POST /chat request body (supports context continuation)

## 5. Types and Utilities

- [x] 5.1 Create `frontend/src/types/conversation.ts` with Conversation interface and utility types
- [x] 5.2 Create `frontend/src/utils/localStorage.ts` with save/load/clear functions for conversations
- [x] 5.3 Add unit tests for localStorage helpers (save, load, edge cases)

## 6. Testing and Polish

- [x] 6.1 Test conversation creation, deletion, and rename
- [x] 6.2 Test search functionality (empty state, partial match, case sensitivity)
- [x] 6.3 Test conversation context switching (load messages, continue chatting)
- [x] 6.4 Test localStorage persistence (refresh page, close/reopen browser)
- [x] 6.5 Test error states (localStorage full, corrupt data recovery)
- [x] 6.6 Verify sidebar responsive behavior on mobile viewports
- [x] 6.7 Test that sidebar active state updates correctly on click
