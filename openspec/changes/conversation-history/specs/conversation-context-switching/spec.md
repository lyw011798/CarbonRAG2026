## ADDED Requirements

### Requirement: Switch between conversations
The system SHALL allow users to click a conversation in the sidebar to load its message history and set it as the active conversation.

#### Scenario: User clicks a conversation
- **WHEN** user clicks on a conversation in the sidebar
- **THEN** the main chat area loads that conversation's message history and sets it as the active conversation

#### Scenario: Message display updates
- **WHEN** a conversation is loaded as active
- **THEN** the chat message area displays all messages from that conversation in chronological order

#### Scenario: Active conversation ID persists in state
- **WHEN** a conversation is clicked
- **THEN** the activeConversationId in app state is updated (and remains active until user clicks a different conversation or creates a new one)

### Requirement: Continue chatting in previous conversations
The system SHALL allow users to submit new messages while viewing and continuing a previous conversation.

#### Scenario: User appends message to old conversation
- **WHEN** user loads an old conversation and types a new message
- **THEN** the new message is appended to that conversation's message history (not started as a new conversation)

#### Scenario: Backend receives appended messages with full context
- **WHEN** user submits a message in an old conversation
- **THEN** the backend `/chat` endpoint receives all prior messages from that conversation as context (full conversation history in the POST body)

#### Scenario: Assistant response added to same conversation
- **WHEN** assistant responds to a message in an old conversation
- **THEN** the response is appended to that conversation and displayed in the main chat area

### Requirement: Updated timestamps reflect activity
The system SHALL update the `updatedAt` timestamp for a conversation whenever a message is added or the title is changed.

#### Scenario: Timestamp updates on new message
- **WHEN** a message is added to a conversation
- **THEN** the conversation's `updatedAt` is set to the current time

#### Scenario: Sidebar sorts by most recent
- **WHEN** conversations are listed in the sidebar
- **THEN** they are ordered by `updatedAt` in descending order (most recent first)

### Requirement: UI maintains focus and scroll context
The system SHALL maintain scroll position and focus within the chat area when switching conversations and ensure auto-scroll to latest message when new messages arrive.

#### Scenario: Auto-scroll on conversation load
- **WHEN** a conversation is loaded
- **THEN** the chat area auto-scrolls to the most recent message

#### Scenario: Auto-scroll on new message
- **WHEN** a new message is appended (user or assistant)
- **THEN** the chat area auto-scrolls to display the latest message
