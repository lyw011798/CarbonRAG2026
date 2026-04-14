## ADDED Requirements

### Requirement: Interactive CLI Remains the Default
The system MUST keep `rag_query.py` as an interactive multi-turn CLI when invoked without a one-time query argument.

#### Scenario: User starts interactive mode
- **WHEN** the user runs `python rag_query.py` with no `--query` argument
- **THEN** the CLI enters the existing conversational loop and accepts multiple turns until the user exits

### Requirement: One-Time Query CLI Mode
The system MUST support a one-time query mode in `rag_query.py` when the user provides `--query`.

#### Scenario: User runs a single query
- **WHEN** the user runs `python rag_query.py --query "你的問題"`
- **THEN** the CLI retrieves relevant context, asks the model one question, prints one answer, and exits

### Requirement: Query Mode Tuning Flags
The system MUST allow the one-time query flow to accept `--top-k` and `--model` options.

#### Scenario: User adjusts retrieval depth and model
- **WHEN** the user runs `python rag_query.py --query "你的問題" --top-k 5 --model gemini-2.5-flash`
- **THEN** the system retrieves the top 5 chunks and uses the specified LiteLLM model for generation

### Requirement: Cited Source Output
The system MUST display a final answer followed by a numbered source list for both interactive and one-time query results.

#### Scenario: Displaying answer and sources
- **WHEN** the CLI produces a response
- **THEN** stdout shows an `Answer:` block, then a `Sources:` block with entries formatted as `[n] <filename>  (section: <section>, score: <score>)`

### Requirement: Language-Aware Response
The system MUST instruct the model to answer in the same language as the user's question.

#### Scenario: User asks in Chinese
- **WHEN** the user submits a question in Chinese
- **THEN** the generated response is also in Chinese unless the model cannot comply