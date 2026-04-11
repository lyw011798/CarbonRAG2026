## ADDED Requirements

### Requirement: Command Line Query Interface
The system MUST provide an interactive CLI tool inside `rag_query.py` that processes human questions and routes them through the RAG pipeline.

#### Scenario: User queries for carbon fee
- **WHEN** the user runs `python rag_query.py` and types "What is the carbon fee rate?"
- **THEN** RAGQuery retrieves relevant context, constructs a prompt for LiteLLM, and prints the generated text

### Requirement: Jurisdiction Specific Prompt Context
RAGQuery MUST prepend a strict Taiwan regulatory system instruction ("from Taiwan regulatory perspective") to all LLM requests to prevent conflation with extraneous international standards.

#### Scenario: Mitigating cross-standard confusion
- **WHEN** context regarding carbon pricing is dispatched to LiteLLM
- **THEN** the system directive forces interpretation exclusively via Taiwan's legal frameworks rather than defaulting to generic global implementations

### Requirement: Cited Source Output
The system MUST surface and display relevant metadata corresponding to the retrieved context accompanying the final answer.

#### Scenario: Displaying citations
- **WHEN** the LLM prints a synthesized response
- **THEN** the CLI additionally outputs the `filename`, `page_num`, and `source` metadata from the referenced ChromaDB chunks
