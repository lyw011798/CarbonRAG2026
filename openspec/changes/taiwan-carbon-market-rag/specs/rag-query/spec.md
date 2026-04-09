## ADDED Requirements

### Requirement: Jurisdiction-aware prompting
The system SHALL inject a specific system prompt stating "from Taiwan regulatory perspective" or equivalent to ensure the LLM responses adhere to the Taiwan jurisdiction when parsing retrieved context.

#### Scenario: Asking a query about carbon border tax
- **WHEN** the user queries about "CBAM implementation"
- **THEN** the system generates a prompt including the Taiwan jurisdiction frame and specifically references EU CBAM interaction with Taiwan's reporting

### Requirement: Source citation
The system SHALL output citations including the source document name and the closest structural section (e.g., Article number).

#### Scenario: Generating an answer
- **WHEN** the user receives an LLM response
- **THEN** the response ends with a citation block such as "Source: Climate Change Response Act, Article 21"
