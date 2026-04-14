## Why

The current data update pipeline in `data_update.py` runs all stages (extract, clean, chunk, embed, store) in sequential order without any fine-grained control. This makes it impossible to pause, resume, or re-run specific stages, making both iterative development and incremental data updates very slow. We need the ability to conditionally control execution on a per-stage basis and bypass reprocessing unchanged files.

## What Changes

- The CLI interface of `data_update.py` will accept a `--stages` argument, specifying exactly which pipeline stages to run out of `extract`, `clean`, `chunk`, `embed`, and `store`.
- The CLI interface will accept a `--rebuild` flag to wipe past artifacts before running.
- The CLI interface will accept a `--dry-run` flag to display intended operations without altering files or the vector DB.
- Incremental update logic will be introduced based on SHA256 hashes of raw file contents, stored in `data/processed/.hashes.json`. Files with unchanged hashes will skip the extraction and cleaning stages.
- The `--rebuild` flag will delete all `data/processed/*.txt` and `data/processed/.hashes.json` files before executing the pipeline.

## Capabilities

### New Capabilities
- `pipeline-stage-control`: Execution logic to selectively run distinct stages (`extract`, `clean`, `chunk`, `embed`, `store`) via the GUI-less CLI interface.
- `incremental-updates`: A state checking system utilizing SHA256 content hashing to bypass extraction and cleaning for unmodified raw files.

### Modified Capabilities
- `cli-interface`: Extend the data parsing application endpoint (`data_update.py`) to parse new command-line parameters (`--stages`, `--rebuild`, `--dry-run`).

## Impact

- **`data_update.py`**: Heavily modified to orchestrate conditional stage processing, calculate content differences from `data/processed/.hashes.json`, and interpret new CLI arguments.
- **Data storage (`data/processed`)**: Will contain a new `.hashes.json` entity that serves as the incremental cache.

## Class Responsibilities

- **`data_update.py`**: Owns CLI argument parsing, incremental state checking against `.hashes.json`, and managing the sequence of pipeline stages.
- **`DocumentProcessor` Subclasses (`PDFProcessor`, `TextProcessor`, `MarkdownProcessor`, `HTMLProcessor`)**: Own the responsibility of interpreting their respective file modalities (.pdf, .txt, .md, .html). They are executed during the `extract` stage.
- **`ChunkStrategy` (`chunker.py`)**: Owns the text splitting logic (the `chunk` stage).
- **`VectorStore` (`store.py`)**: Owns embedding vectors and saving to ChromaDB (the `embed` and `store` stages), filtering out document chunks that are already embedded.

## Non-goals

- Parallel or asynchronous stage execution.
- Remote storage backends (e.g., S3, Google Cloud Storage, remote databases).
- Implementing a GUI or web interface for pipeline configuration or orchestration.
