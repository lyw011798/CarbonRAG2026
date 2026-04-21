## 1. Strategy Detection Optimization

- [x] 1.1 Update `ChunkStrategy._detect_strategy()` in `src/chunker.py`: Modify the legal detection threshold to require `len(legal_matches) >= 3` to avoid eager chunking.

## 2. Chunk Limit Adjustments

- [x] 2.1 Update `ChunkStrategy.__init__()` in `src/chunker.py`: Change the default parameter `max_chunk_size` from 2000 to 250.
- [x] 2.2 Update `ChunkStrategy.__init__()` in `src/chunker.py`: Change the default parameter `overlap_lines` from 1 to 2.

## 3. Pipeline Extraction Verification

- [x] 3.1 Validate chunk output generated specifically by tests involving `PDFProcessor` (`src/processors/pdf.py`).
- [x] 3.2 Validate chunk output generated specifically by tests involving `TextProcessor` (`src/processors/text.py`).
- [x] 3.3 Validate chunk output generated specifically by tests involving `MarkdownProcessor` (`src/processors/markdown.py`).
- [x] 3.4 Validate chunk output generated specifically by tests involving `HTMLProcessor` (`src/processors/html.py`).

## 4. Rebuild Vector Store

- [x] 4.1 Run the ingestion pipeline utilizing the new chunker settings (`python data_update.py --rebuild`) to repopulate the ChromaDB instance.
