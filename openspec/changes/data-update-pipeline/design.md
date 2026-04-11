## Context

Our data processing pipeline in `data_update.py` utilizes the Strategy Pattern via `DocumentProcessor` subclasses, processing heterogeneous file formats (.pdf, .txt, .md, .html) into text. It then chunks the text (`ChunkStrategy`), embeds it, and stores the vectors in a ChromaDB `VectorStore`. Currently, this acts as a monolithic, serial execution over all files. The lack of a mechanism to resume from intermediate stages or skip unchanged files causes considerable inefficiency during iterative development and routine data ingestion. This design outlines the implementation of stage-level control and incremental processing based on file hashes.

## Goals / Non-Goals

**Goals:**
- Provide clear, isolated functional boundaries for the five stages: `extract`, `clean`, `chunk`, `embed`, and `store`.
- Enhance the CLI (`data_update.py`) to accept an array of `--stages` to execute selectively.
- Maintain an incremental state file (`data/processed/.hashes.json`) that saves SHA256 hashes of the raw `data/raw/*` input files.
- Bypass the `extract` and `clean` portions of the pipeline for unchanged files by comparing current file hashes with the state file.
- Introduce a `--rebuild` flag to purge all existing text artifacts and cache hashes, offering a fresh pipeline start.
- Provide a `--dry-run` parameter to preview system actions, particularly which files will be skipped without mutating state.

**Non-Goals:**
- Concurrency, parallelism, or asynchronous execution mechanics.
- Integration or deployment of external/remote storage layers (e.g., AWS S3).
- Creation of GUI or web-based dashboards for pipeline configuration.
- Adjusting the text extraction routines of `pdfplumber`, `beautifulsoup4`, or other underlying libraries.

## Decisions

**1. CLI Argument Parsing and Orchestration (`data_update.py`)**
*Rationale*: We will utilize Python's standard `argparse` to interpret the `--stages`, `--rebuild`, and `--dry-run` inputs. The main module will orchestrate the phases by looping over files and applying stages chronologically filtering files dependent on their hash values.
*Alternative*: Building a declarative YAML config pipeline was considered but discarded in favor of simplicity; CLI args provide the tightest, lowest friction developer loop.

**2. Incremental Caching Strategy**
*Rationale*: A dictionary structure associating `{ "filepath": "sha256_hash" }` will be dynamically JSON-serialized into `data/processed/.hashes.json`. During iteration, if a file's hash hasn't changed, the pipeline skips `extract` and `clean` for that subset.
*Alternative*: Storing update hashes within ChromaDB metadata. This was rejected because the vector store operates at the chunk level, not the raw file level, and using a simple JSON proxy is considerably lighter weight for the extraction phase check.

**3. Idempotent Sinks**
*Rationale*: 
- The `clean` stage modifies text files in place. 
- The `store` stage must verify if a specific `chunk_id` corresponds to an existing ChromaDB vector before proceeding with insertion. This acts as the skip condition.

## Risks / Trade-offs

- **[Risk] State corruption:** Manual manipulation or corruption of `.hashes.json` could skew expected execution. 
  - *Mitigation*: The `data_update.py` script will be resilient. If the JSON cache is unparseable or corrupted, it will default to rebuilding the state.
- **[Risk] Stage interdependency:** The `embed` and `store` stages expect in-memory `chunks` and `vectors`. If a user calls `python data_update.py --stages embed store`, the pipeline must load files into memory. 
  - *Mitigation*: The `data_update.py` script state machine will be designed to load existing pre-processed outputs from `data/processed/*.txt` if generation stages (like `extract`) are bypassed.
- **[Risk] Ghost records in VectorStore:** If a source document shrinks or is deleted, checking `chunk_id` exists does not prune old chunks. 
  - *Mitigation*: Handled on a standard rebuild (`--rebuild`), wiping the store entirely, keeping the pipeline logic simple for incremental additions.
