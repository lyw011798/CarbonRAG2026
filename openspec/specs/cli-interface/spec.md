## ADDED Requirements

### Requirement: Sub-command Execution CLI
The `data_update.py` script SHALL handle command-line parameters to set pipeline stages, rebuild state, and perform dry runs.

#### Scenario: Providing stage flags
- **WHEN** the user executes `python data_update.py --stages extract clean`
- **THEN** the system parses the `extract` and `clean` inputs and activates only those stages.

#### Scenario: Default run enables all stages
- **WHEN** the user executes `python data_update.py`
- **THEN** all stages (`extract`, `clean`, `chunk`, `embed`, `store`) are enabled by default.

#### Scenario: Providing rebuild flag
- **WHEN** the user executes `python data_update.py --rebuild`
- **THEN** the system triggers the cache purging mechanism before processing all stages.

#### Scenario: Providing dry-run flag
- **WHEN** the user executes `python data_update.py --dry-run`
- **THEN** the system evaluates hash checks and outputs what would be processed without mutating any files or the vector database.
