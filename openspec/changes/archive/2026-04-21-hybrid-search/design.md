## Context

The current `VectorStore` uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` instantiated via ChromaDB's built-in `SentenceTransformerEmbeddingFunction`. Retrievals perform symmetric similarity math on semantic space. This mechanism fundamentally hides highly-specific structured answers (like numerical tables) when queried with natural-language questions. To resolve this, replacing the model with `intfloat/multilingual-e5-small` paired with a BM25 keyword index is proposed. E5 models require instruction prefixes (`passage: ` and `query: `) to correctly map asymmetric spaces, and BM25 requires tokenized word arrays to build its document frequency maps.

## Goals / Non-Goals

**Goals:**
*   Implement a transparent pipeline that proxies E5 instruction prefixes before they hit the embedding algorithm.
*   Implement a `rank_bm25` pipeline backed by `jieba` tokenization to establish exact-match retrieval indexing alongside ChromaDB.
*   Combine Dense (Chroma) and Sparse (BM25) metrics in `RAGQuery` using Reciprocal Rank Fusion (RRF).

**Non-Goals:**
*   Adding complex ElasticSearch or external database layers (BM25 will be serialized locally using lightweight pickling or dynamically rebuilt).

## Decisions

### Decision 1: Model Substitution and Instruction Architecture
**Rationale:** We will replace the default `model_name` parameter to `intfloat/multilingual-e5-small`. Because ChromaDB hides the `encode()` call inside its native `SentenceTransformerEmbeddingFunction`, we will create a lightweight subclass or wrapper `InstructionEmbeddingFunction` that prepends `"passage: "` for documents and `"query: "` to inputs based on the calling context. (Alternatively, prepending `"query: "` at the start of the `RAGQuery` text might be simpler and sufficient).
**Alternative:** Altering `text` directly before `add_documents`. Rejected because the word "passage:" would leak into the LLM context or RAG citations.

### Decision 2: BM25 Storage Mechanism
**Rationale:** We will use `jieba.lcut` to tokenize Chinese chunks, then feed them to `rank_bm25.BM25Okapi`. When `VectorStore` persists via its existing workflow, we will pickle the BM25 object to `$db_path/bm25.pkl` alongside ChromaDB's SQLite database. When `VectorStore` instantiates, it will load this pickle file if present.
**Alternative:** Storing BM25 terms inside Chroma metadata. Rejected as it is highly inefficient to compute IDF counts dynamically from metadata.

### Decision 3: Reciprocal Rank Fusion Logic
**Rationale:** In `RAGQuery.retrieve()`, we will pull the `top_k * 2` documents from BM25 and the `top_k * 2` documents from ChromaDB, then combine their reciprocal ranks: `Score = 1 / (k + rank)`. Then we will sort and return the definitive `top_k` chunk IDs.

## Risks / Trade-offs

*   **[Risk] Increased Build Time** → **[Mitigation]** `jieba` tokenization is CPU-bound and will slow down `data_update.py`. Since ingestion is offline, this performance hit is acceptable.
*   **[Risk] Stale BM25 Indices** → **[Mitigation]** If the user deletes SQLite files but forgets to delete the `bm25.pkl` file, discrepancies could occur. Our implementation must verify the BM25 index length against the Chroma collection size to detect desyncs.
