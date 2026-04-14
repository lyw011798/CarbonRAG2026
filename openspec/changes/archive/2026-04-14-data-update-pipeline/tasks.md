## 1. CLI and State Configuration

- [x] 1.1 Implement `argparse` in `data_update.py` to support `--stages` (list), `--rebuild` (boolean), and `--dry-run` (boolean).
- [x] 1.2 Create a state management function in `data_update.py` to read and write SHA256 hashes from/to `data/processed/.hashes.json`.
- [x] 1.3 Implement a reset function in `data_update.py` that clears `data/processed/*.txt` and `.hashes.json` when the `--rebuild` flag is passed.

## 2. Selective Extraction per Format

- [x] 2.1 Refactor the `PDFProcessor` extraction logic block in `data_update.py` to skip if the hash matches the cache state.
- [x] 2.2 Refactor the `TextProcessor` extraction logic block in `data_update.py` to skip if the hash matches the cache state.
- [x] 2.3 Refactor the `MarkdownProcessor` extraction logic block in `data_update.py` to skip if the hash matches the cache state.
- [x] 2.4 Refactor the `HTMLProcessor` extraction logic block in `data_update.py` to skip if the hash matches the cache state.
- [x] 2.5 Isolate the `clean` text utility stage in `data_update.py` to execute conditionally based on the `--stages clean` list inclusion.

## 3. Mid-Pipeline State Loading

- [x] 3.1 Implement a data loader function in `data_update.py` that sequentially reads all `data/processed/*.txt` files into memory to bootstrap later stages if `extract` is omitted.
- [x] 3.2 Encapsulate the chunking loop in `data_update.py` to only execute if `chunk` is present in the pipeline stages arguments.

## 4. Idempotent Vector Handling

- [x] 4.1 Add an existence check in `VectorStore.add_chunks()` within `store.py` to query ChromaDB for the `chunk_id` before embedding and inserting.
- [x] 4.2 Isolate the `embed` and `store` trigger logic in `data_update.py` to only execute if requested in `--stages`.
- [x] 4.3 Apply the `--dry-run` condition wrap across the script to intercept and print actions instead of writing to disk or database.
