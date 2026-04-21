## Why

The current RAG system fails to answer specific questions accurately because relevant segments of documents (e.g., fee rate tables at the end of a summary document) are silently truncated. This is caused by two overlapping issues: the `ChunkStrategy` mistakenly classifies non-legal documents as legal documents due to a single stray "第X條" match resulting in a massive >2000 character chunk, and the embedding model (`paraphrase-multilingual-MiniLM-L12-v2`) natively truncates any input over 128 tokens, meaning content near the end of a chunk is never embedded. By correcting the chunking logic and size, we ensure all context across all supported document types (.pdf, .txt, .md, .html) is correctly embedded and retrievable.

## What Changes

* Modify `ChunkStrategy._detect_strategy` to use stricter regular expressions or require multiple matches (e.g., `>= 3`) before classifying a document as 'legal' (Strategy 1).
* Reduce `max_chunk_size` in `ChunkStrategy` from 2000 to 250 characters to align with the underlying sentence-transformer token limit (128 tokens) without silent truncation.
* Enhance `ChunkStrategy._basic_sub_chunk` to ensure short, highly relevant chunks (250 chars) while properly propagating header metadata to retain context.

## Capabilities

### New Capabilities
- `chunk-optimization`: Introduces stricter strategy detection rules and smaller maximum chunk sizes to prevent silent embedding truncation.

### Modified Capabilities
- 

## Impact

* **Code Impact**: Modifies `src/chunker.py`'s `ChunkStrategy` and alters how chunks are produced.
* **Architecture**: The `data_update.py` pipeline remains the same, but the resulting chunks added to ChromaDB will be much smaller and numerous. As a requirement, the database will need to be rebuilt using `--rebuild`.
* **Data Pipelines**: Changes impact content extraction from all file formats (.pdf, .txt, .md, and .html), ensuring tables and footnotes previously lost in large chunks are preserved.

## Non-goals
* This proposal does *not* aim to replace the embedding model (`paraphrase-multilingual-MiniLM-L12-v2`); we are adapting to its limits rather than deploying a completely new model.
* This does *not* modify the extraction logic in `pdf.py`, `text.py`, `markdown.py`, or `html.py`.
