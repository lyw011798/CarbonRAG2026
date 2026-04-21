
### Requirement: E5 Instruction Embedding Overrides
The system SHALL intercept raw document text and queries to safely prepend correct E5 model instructions before ChromaDB's underlying embeddings execute.

#### Scenario: Submitting semantic query
- **WHEN** user query is processed by `RAGQuery` or the internal `VectorStore.query` method
- **THEN** the system modifies the prompt string prefix explicitly with `"query: "` before semantic measurement occurs, returning optimal proximity against target chunk spaces prefixed with `"passage: "`.
