## ADDED Requirements

### Requirement: Automated Domain Skill Synthesis
The SkillBuilder MUST automatically query the underlying RAG system across predefined critical domain topics (e.g., Core Concepts, Entities, Current Status) to compile knowledge.

#### Scenario: Compiling knowledge sections
- **WHEN** `skill_builder.py` is invoked
- **THEN** iterative RAG queries are evaluated, extracting definitions and statuses referencing TCX, MOENV, and CBAM protocols

### Requirement: Exporting generated artifact
The SkillBuilder MUST successfully synthesize the responses into the structure of a markdown agent-skill reference document.

#### Scenario: Finalizing build
- **WHEN** the knowledge aggregation resolves
- **THEN** the system generates and saves an offline `skill.md` file intended for usage by autonomous AI agents
