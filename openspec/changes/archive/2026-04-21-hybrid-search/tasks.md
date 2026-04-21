## 1. Environment Setup

- [x] 1.1 Update `requirements.txt`: Add `rank_bm25` and `jieba`.
- [x] 1.2 Install new dependencies into the current Python environment using `pip install -r requirements.txt`.

## 2. Model Override and Prefixes

- [x] 2.1 Update `VectorStore.__init__` (`src/store.py`): Change default embedding string to `intfloat/multilingual-e5-small`.
- [x] 2.2 Implement `InstructionEmbeddingFunction` (`src/store.py`): Wrap the base embedding function to inject `"passage: "` during `add_documents` and `"query: "` during query execution.

## 3. Sparse BM25 Integration

- [x] 3.1 Update `VectorStore.add_documents` (`src/store.py`): Create the BM25Okapi index using `jieba` tokenization on newly ingested chunk text, and save to `bm25.pkl` in `db_path`.
- [x] 3.2 Update `VectorStore.__init__` (`src/store.py`): Automatically load `bm25.pkl` into memory if it exists.
- [x] 3.3 Implement `VectorStore.query_bm25` (`src/store.py`): Return the top K document IDs based on sparse BM25 token matches.

## 4. Hybrid Retrieval & Reciprocal Rank Fusion

- [x] 4.1 Update `RAGQuery.query` or `RAGQuery.retrieve` (`src/query.py`): Request `top_k * 2` results from both BM25 and Semantic search, calculate `1 / (60 + rank)`, and return the definitive combined `top_k` documents.

## 5. Verification and Rebuild

- [x] 5.1 Run `python data_update.py --rebuild` to wipe the old purely dense database, generate the E5 dimensions, and serialize the BM25 objects.
- [x] 5.2 Verify dual-search functionality specifically against data extracted via `TextProcessor`.
- [x] 5.3 Verify dual-search functionality specifically against data extracted via `HTMLProcessor`.
- [x] 5.4 Verify dual-search functionality specifically against data extracted via `MarkdownProcessor`.
- [x] 5.5 Verify dual-search functionality specifically against data extracted via `PDFProcessor`.
