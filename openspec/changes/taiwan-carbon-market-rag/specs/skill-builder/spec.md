## ADDED Requirements

### Requirement: Automated skill manual generation
The system SHALL generate a markdown file (`skill.md`) synthesizing core concepts, key entities, current status, and common Q&A by querying the compiled vector store on predefined topics.

#### Scenario: Running the skill builder script
- **WHEN** the user runs `skill_builder.py`
- **THEN** a `skill.md` file is generated containing sections for "Overview", "Core Concepts", "Key Entities", "Current Status", and "Common Q&A"
