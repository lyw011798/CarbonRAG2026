## Context

The RAG pipeline extracts text from documents (.pdf, .txt, .md, .html) and delegates chunking to `ChunkStrategy`. `ChunkStrategy` relies on regex patterns to detect document types and sub-divide texts based on "Legal Articles", "Numbered Sections", etc. If chunks exceed `max_chunk_size` (currently 2000), they fall back to paragraph-based sub-chunking.

During retrieval, ChromaDB embeds chunks via the `paraphrase-multilingual-MiniLM-L12-v2` SentenceTransformer model. However, this model has a `max_seq_length` of roughly 128 tokens. This severe mismatch between the chunker's 2000-character max limit and the ~150-200 character embedding window means the tail ends of large chunks are permanently lost during vector creation. Additionally, minor formatting artifacts (e.g., text wrappers starting lines with "第二十八條") trigger the "Legal Article" chunk strategy prematurely exactly once, effectively treating an entire document as a single massive legal article chunk.

## Goals / Non-Goals

**Goals:**
*   Prevent vector truncation by aligning `max_chunk_size` with the embedding model's actual context window constraints.
*   Prevent false positives in chunk strategy detection, particularly for the 'legal' strategy.
*   Preserve context properly across multiple smaller chunks.

**Non-Goals:**
*   Swapping out the embedding model for one with a larger context window (e.g., `multilingual-e5-large` or OpenAI embeddings).
*   Refactoring the upstream text extractors (PDF, HTML, etc.).

## Decisions

### Decision 1: Reduce `max_chunk_size` limits
**Rationale:** The embedding model silently truncates inputs larger than 128 tokens. A `max_chunk_size` of 250 characters ensures that the vast majority of extracted chunks fit cleanly into the semantic window of the embedding model without dropping crucial text (like tables at the end of sections).
**Alternative:** Change the embedding model. This was rejected because it introduces new dependencies or API costs, deviating from the current local-first approach.

### Decision 2: Strengthen Strategy Detection for Legal Documents
**Rationale:** The current trigger `if len(legal_matches) >= 1: return 'legal'` is too eager. A single reference to a legal article code within a standard summary document will cause the chunker to mistakenly classify the format. By changing the threshold to `if len(legal_matches) >= 3:`, we ensure the document is actually a legal compendium containing multiple articles.
**Alternative:** Enforcing rigid start-of-document anchors. This was rejected because parsed PDFs often contain introductory text or tables of contents before the first article.

### Decision 3: Increase overlap lines
**Rationale:** Since chunks are now significantly smaller (250 chars), the probability of splitting related sentences increases. By changing `overlap_lines` from 1 to 2 in the `ChunkStrategy` constructor (or fallback logic), we provide slightly more connective tissue between contiguous chunks.

## Risks / Trade-offs

*   **[Risk] Increased Vector Store Size** → **[Mitigation]** Smaller chunks will result in significantly more entries in ChromaDB. The storage scale for Taiwan carbon documents is small enough that this overhead is completely manageable locally.
*   **[Risk] Semantic Fragmentation** → **[Mitigation]** Reducing chunk size makes context fragmented. The `_basic_sub_chunk` method already injects the structural header/context logic (e.g., `[第三章] ... `) into every sub-chunk, which mitigates fragmentation.
