## ADDED Requirements

### Requirement: Store and retrieve conversations in localStorage
The system SHALL persist conversations to browser localStorage under the key `carbonrag-conversations` and load them on app startup.

#### Scenario: App loads with existing conversations
- **WHEN** user opens the app and localStorage contains prior conversations
- **THEN** the app loads all conversations into memory without making a backend request

#### Scenario: App loads with no prior conversations
- **WHEN** user opens the app and localStorage is empty or contains no conversations
- **THEN** the app initializes with an empty conversation list (sidebar shows no items)

### Requirement: Create new conversations
The system SHALL auto-generate a new blank conversation object each time the app loads, with a unique ID and timestamp.

#### Scenario: Auto-create on load
- **WHEN** the app loads (regardless of existing conversations)
- **THEN** a new blank conversation is created with ID (UUID), title "New Chat", empty messages array, and current timestamp

#### Scenario: New conversation becomes active
- **WHEN** a new conversation is auto-created
- **THEN** it is immediately set as the active conversation for chat input and message display

### Requirement: Delete conversations
The system SHALL allow deletion of conversations from localStorage, removing them from the sidebar immediately.

#### Scenario: User deletes a conversation
- **WHEN** user clicks delete button on a conversation in the sidebar
- **THEN** the conversation is removed from localStorage and disappears from the sidebar

#### Scenario: Delete active conversation
- **WHEN** user deletes the currently active conversation
- **THEN** the system switches to the most recent remaining conversation, or creates a new one if none remain

### Requirement: Rename conversations
The system SHALL allow users to edit conversation titles and persist changes to localStorage.

#### Scenario: User renames a conversation
- **WHEN** user clicks rename button, enters new title, and confirms
- **THEN** the conversation title is updated in localStorage and reflected immediately in the sidebar

### Requirement: Persist messages to active conversation
The system SHALL append each user message and assistant response to the active conversation and sync the updated state to localStorage.

#### Scenario: User sends a message
- **WHEN** user submits a message in chat
- **THEN** the message is appended to the active conversation's messages array and localStorage is updated

#### Scenario: Assistant responds
- **WHEN** assistant generates a response
- **THEN** the response is appended to the active conversation's messages array and localStorage is updated
