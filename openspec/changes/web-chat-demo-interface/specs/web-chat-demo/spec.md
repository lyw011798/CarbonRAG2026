## ADDED Requirements

### Requirement: Chat Layout
The system MUST provide a single-page React chat interface with a polished ChatGPT-like layout.

#### Scenario: User opens the demo
- **WHEN** the user opens the web chat demo
- **THEN** the system displays a clean responsive chat page with a header, message area, and input composer

#### Scenario: No messages exist
- **WHEN** the conversation has no messages
- **THEN** the system displays an empty state that explains the demo purpose and invites the user to ask a question

### Requirement: Message History
The system MUST show the current browser-session conversation history in chronological order.

#### Scenario: User sends a message
- **WHEN** the user submits a non-empty chat message
- **THEN** the system appends the user message to the visible conversation immediately

#### Scenario: Assistant response is received
- **WHEN** the chat API returns an assistant response
- **THEN** the system appends the assistant message after the user message

### Requirement: Chat API Integration
The system MUST send chat requests to `POST /chat` and render the returned assistant message.

#### Scenario: Successful chat request
- **WHEN** the user submits a message and `POST /chat` returns a valid assistant message
- **THEN** the system displays the assistant response in the conversation

#### Scenario: API request payload
- **WHEN** the system sends a chat request
- **THEN** the request body includes the visible conversation messages needed by the API to answer the latest user message

### Requirement: Loading State
The system MUST show a loading state while a chat request is in progress.

#### Scenario: Request is pending
- **WHEN** the user submits a message and the API request has not completed
- **THEN** the system disables duplicate submission and displays a visible assistant loading indicator

#### Scenario: Request completes
- **WHEN** the API request succeeds or fails
- **THEN** the system removes the loading indicator and re-enables message submission when valid input exists

### Requirement: Explicit Error Handling
The system MUST show descriptive error feedback when chat submission fails.

#### Scenario: Network or server failure
- **WHEN** the chat API request fails because of a network error or non-successful HTTP response
- **THEN** the system displays a descriptive error message without removing existing conversation messages

#### Scenario: Malformed API response
- **WHEN** the chat API returns a response that does not contain a valid assistant message
- **THEN** the system displays a descriptive error message explaining that the response could not be read

### Requirement: Auto Scroll
The system MUST automatically scroll the message area to the latest conversation state.

#### Scenario: New message appears
- **WHEN** a user message, assistant message, loading indicator, or error state is added to the conversation area
- **THEN** the system scrolls the message area to the newest visible item

### Requirement: Maintainable Frontend Structure
The system MUST organize frontend code into typed models, API integration, chat state, and presentational components.

#### Scenario: Developer reviews the frontend
- **WHEN** a developer inspects the frontend implementation
- **THEN** chat API calls, chat state management, message types, and UI components are separated into focused files with strong TypeScript typing

### Requirement: Minimal Polished Design
The system MUST use Tailwind styling to provide a minimal but polished user experience.

#### Scenario: User interacts with the demo
- **WHEN** the user reads messages, types input, submits a message, waits for a response, or sees an error
- **THEN** the visual design remains clear, accessible, and consistent across common desktop and mobile viewport sizes
