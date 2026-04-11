## Context

Taiwan formally entered the carbon pricing era in 2025. Tracking rapid regulatory changes across the Ministry of Environment (MOENV), Taiwan Carbon Solution Exchange (TCX), and Climate Change Administration (CCA) requires structured knowledge extraction. Official government sources come in diverse formats including table-heavy PDFs, legacy BIG5 text files, Markdown files, and raw HTML pages. This project proposes a localized CLI Retrieval-Augmented Generation (RAG) pipeline specialized for the Taiwan carbon market capable of seamlessly handling these multi-format documents.

## Goals / Non-Goals

**Goals:**
- Construct an efficient local vector database containing Taiwanese carbon pricing policies and rules.
- Support 4 raw file formats (.pdf, .txt, .md, .html) with dedicated parse cleaning logic.
- Implement the Strategy Pattern (via `DocumentProcessor` subclasses) and Factory Pattern (`ProcessorFactory`) to handle diverse document formats cleanly.
- Design Python classes with explicit boundaries to strictly parse complex documents and legal articles ("第X條") using local embeddings (`sentence-transformers`).
- Generate an exportable `skill.md` context document as an AI expert file based on RAG synthesis.

**Non-Goals:**
- No graphical interface; purely CLI tools.
- No third-party closed-source embeddings.
- No general-purpose domain support outside of Taiwan's carbon jurisdiction.

## Decisions

### Architecture Class Diagram

```ascii
+----------------+       +-------------------+
| data_update.py | ----> | ProcessorFactory  | 
+----------------+       | (src/processors/  |
          |              |       factory.py) |
          |              +-------------------+
          |                        | resolves
          v                        v
+----------------+       +-------------------------+      +-----------------+
| ChunkStrategy  | <---- | DocumentProcessor (ABC) | ---> | VectorStore     |
| (src/chunker.py|       | (src/processors/base.py)|      | (src/store.py)  |
+----------------+       +-------------------------+      +-----------------+
                                     ^ 
                                     | inherits                  ^
          +--------------------------+-----------------+         |
          |               |                |           |         |
+----------------+ +---------------+ +-------------+ +-------------+
| PDFProcessor   | | TextProcessor | | HTMLProcessor | | MDProcessor |
| (pdf.py)       | | (text.py)     | | (html.py)   | | (markdown.py|
+----------------+ +---------------+ +-------------+ +-------------+
          
+----------------+                                   
| rag_query.py   | <-----------------------------------------+
+----------------+                                           |
       |                                                     v
       v                                              +----------------+
+----------------+                                    | RAGQuery       |
| builder.py     | <--------------------------------- | (src/query.py) |
| (SkillBuilder) |                                    +----------------+
+----------------+                                           
```

### Class Boundaries & Justifications

We strictly employ moderate OOP by creating classes for components possessing distinct state and behaviors, avoiding deep inheritance.

1.  **DocumentProcessor Hierarchy & ProcessorFactory**: 
    - **Decision:** Use Strategy Pattern for diverse file formats with a basic `ProcessorFactory`.
    - **Justification:** Different files have highly specific cleaning challenges (e.g. BS4 vs PDFPlumber). Encapsulating these in separate `DocumentProcessor` subclasses adhering to the basic ABC prevents a massive `if-else` block in `data_update.py`. The `ProcessorFactory` isolates the file extension resolution logic.
2.  **ChunkStrategy**: Requires state tracking concerning legal article structures (e.g., remembering the current "第X條" chapter hierarchy while iterating through text blocks) and appending `valid_date` context to each block.
3.  **VectorStore**: Contains persistent connection wrappers for ChromaDB. Retains the local embedding model (`sentence-transformers`) initialized in memory to avoid repeated loading overhead per batch.
4.  **RAGQuery**: Maintains configuration state for LiteLLM usage (active conversational context, tokens, system formatting instructions).
5.  **SkillBuilder**: Carries accumulation state across consecutive query evaluations before synthesizing the final sections of `skill.md`.

### Format-Specific Cleaning Challenges
Each processor subclass handles unique cleaning rules to sanitize text prior to chunking:
- **PDF (`PDFProcessor`)**: Extracts tables effectively into natural sentences. Strips noisy repeating page headers/footers to preserve text flow.
- **TXT (`TextProcessor`)**: Includes strict file encoding detection since old official documents are often in `BIG5` rather than `UTF-8`.
- **MD (`MarkdownProcessor`)**: Strips excess raw Markdown syntax but strictly tracks and preserves the `# Heading` hierarchy to inject as contextual strings into the final chunks.
- **HTML (`HTMLProcessor`)**: Utilizes `beautifulsoup4` to selectively extract the main body text while aggressively removing noisy `<nav>`, `<footer>`, `<script>`, and `<style>` tags.

## Risks / Trade-offs

-   **Risk:** `pdfplumber` may silently fail on non-standard, incorrectly formatted tables from official government PDFs. -> **Mitigation:** Fallback to PyMuPDF raw text extraction accompanied by warning logs requesting manual checks.
-   **Risk:** Tokenizing long statutory articles may exceed token chunk limits for local `sentence-transformers`. -> **Mitigation:** Implement sub-chunking constraints prioritizing splits at period boundaries while always retaining the article header string in the block.
-   **Trade-off:** Maintaining 4 separate parsers increases testing surface area compared to utilizing a single general document reader (like unstructured.io), but allows for surgical tuning highly specialized for Taiwan's government doc standards.
