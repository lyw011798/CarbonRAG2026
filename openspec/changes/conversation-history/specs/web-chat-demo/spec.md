## MODIFIED Requirements

### Requirement: Message History
The system MUST show the active conversation's message history in chronological order, persisted in localStorage and loadable across browser sessions.

#### Scenario: User sends a message
- **WHEN** the user submits a non-empty chat message in the active conversation
- **THEN** the system appends the user message to the active conversation's message history in localStorage

#### Scenario: Assistant response is received
- **WHEN** the chat API returns an assistant response
- **THEN** the system appends the assistant message to the active conversation and persists it to localStorage

#### Scenario: User switches to previous conversation
- **WHEN** the user clicks on a previous conversation in the sidebar
- **THEN** the system loads that conversation's messages and displays them in chronological order

#### Scenario: Conversation history survives reload
- **WHEN** the user closes and reopens the browser or refreshes the page
- **THEN** the system restores all prior conversations from localStorage, including the messages in each conversation
