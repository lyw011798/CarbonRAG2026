## Why

The current RAG implementation uses a purely symmetric semantic search model (`paraphrase-multilingual-MiniLM-L12-v2`). This heavily struggles with asymmetric retrieval tasks—such as mapping a short user question to a raw data text chunk or structured table row—and completely ignores exact lexical matches. For example, when searching for specific integers like "300" in a table about "一般費率", the symmetric model generates lower scores than long narrative English text, burying the actual answer. By upgrading the embedding model to an instruction-tuned model and combining it with a classical BM25 sparse keyword retriever (Hybrid Search), we can solve this asymmetric mismatch and hit exact keyword constraints across all incoming documents (.pdf, .txt, .md, .html).

## What Changes

* **Model Override**: Switch the default model from `paraphrase-multilingual-MiniLM-L12-v2` to `intfloat/multilingual-e5-small` inside the `VectorStore` class.
* **Instruction Tweaks**: Add `"passage: "` prefix when embedding text to ChromaDB, and `"query: "` prefix when asking a question. `VectorStore` will own the `"passage: "` addition, while `RAGQuery` will own `"query: "`.
* **Sparse Indexer (BM25)**: Integrate `rank_bm25` to index the raw chunk database so exact noun and number keyword matches score highly. `VectorStore` manages loading/saving the BM25 index.
* **Reciprocal Rank Fusion (RRF)**: Implement an integrated scoring pipeline inside `RAGQuery.retrieve()` that merges BM25 keyword ranks and ChromaDB conceptual ranks for optimum context retrieval.

## Capabilities

### New Capabilities
- `hybrid-retrieval`: Implementation of BM25 local indexing and Reciprocal Rank Fusion algorithmic merging.
- `model-upgrade`: Replacement of the dense sentence transformer and implementation of E5 architecture specific instructional string pre-processing.

### Modified Capabilities
- 

## Impact

* **Code Impact**: Modifies `src/store.py` (adding BM25 index builder, changing default model name) and `src/query.py` (introducing dual-search retrieval logic).
* **Dependencies**: Requires `rank_bm25` string tokenization overhead to establish the sparse word index.
* **Database**: Requires completely rebuilding the vector ChromaDB because we are fundamentally hot-swapping the core underlying embedding logic to an E5 dimensional space.

## Non-goals

* **LLM Engine Change**: We will not change `gemini-2.5-flash` to a different backbone.
* **Extraction Overhauls**: We will not alter `ChunkStrategy`, or modify how `.pdf`, `.txt`, `.md`, or `.html` formats are read from disk.
* **Large Embedding Model deployment**: We will explicitly avoid huge LLMs like `BGE-m3` or `multilingual-e5-large` to preserve low RAM/VRAM local grading capability.
