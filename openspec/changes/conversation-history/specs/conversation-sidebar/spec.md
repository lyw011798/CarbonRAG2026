## ADDED Requirements

### Requirement: Display conversation list in sidebar
The system SHALL render a left sidebar showing all conversations as a vertically scrollable list with titles and actions.

#### Scenario: Sidebar displays multiple conversations
- **WHEN** the app has multiple saved conversations
- **THEN** the sidebar displays them as a list sorted by most recently updated first

#### Scenario: Sidebar displays empty state
- **WHEN** no conversations exist
- **THEN** the sidebar displays an empty message (e.g., "No conversations yet")

### Requirement: Search conversations by title
The system SHALL provide a search input in the sidebar that filters conversations in real-time by title substring matching.

#### Scenario: Search filters conversations
- **WHEN** user types in the search box
- **THEN** sidebar displays only conversations whose titles contain the search string (case-insensitive)

#### Scenario: Search clears
- **WHEN** user clears the search box
- **THEN** all conversations are displayed again

### Requirement: Delete conversation from sidebar
The system SHALL provide a delete button on each conversation item that removes it from localStorage and the UI.

#### Scenario: Delete button removes conversation
- **WHEN** user clicks the delete button on a conversation
- **THEN** the conversation is deleted and removed from the sidebar immediately

### Requirement: Rename conversation from sidebar
The system SHALL provide a rename button on each conversation item that allows inline editing of the title.

#### Scenario: Rename button enables editing
- **WHEN** user clicks the rename button on a conversation
- **THEN** an input field appears allowing the user to edit the title

#### Scenario: Confirm rename
- **WHEN** user confirms the new title (by pressing Enter or clicking confirm)
- **THEN** the title is updated in localStorage and the sidebar reflects the change

#### Scenario: Cancel rename
- **WHEN** user presses Escape or clicks cancel while editing a title
- **THEN** the title reverts to the previous value and edit mode closes

### Requirement: New Chat button
The system SHALL display a prominent button in the sidebar to create a new conversation.

#### Scenario: New Chat button creates conversation
- **WHEN** user clicks the "New Chat" or "+" button
- **THEN** a new blank conversation is created, set as active, and appears at the top of the sidebar

### Requirement: Highlight active conversation
The system SHALL visually distinguish the currently active conversation in the sidebar.

#### Scenario: Active conversation is highlighted
- **WHEN** a conversation is active (its messages are displayed in the main area)
- **THEN** the conversation item in the sidebar is highlighted (e.g., different background color or border)

### Requirement: Sidebar styling and responsiveness
The system SHALL style the sidebar to match the existing dark theme and be responsive to screen size.

#### Scenario: Sidebar theme
- **WHEN** the app renders
- **THEN** the sidebar uses the same dark gradient background and typography as the main chat area

#### Scenario: Sidebar on mobile
- **WHEN** viewport width is small (mobile)
- **THEN** the sidebar is either hidden, collapsible, or takes full width appropriately (design TBD in implementation)
