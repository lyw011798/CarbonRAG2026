## Context
Taiwan formally entered the carbon pricing era in 2025. A localized Retrieval-Augmented Generation (RAG) system is needed to aggregate official policy documents, regulations, and market data to enable structured Q&A over this rapidly evolving domain.
Key challenges include document temporality (regulations change), table-heavy PDFs (carbon fee rate tables), structural chunking (article/section boundaries), and prompt framing (jurisdiction).

## Goals / Non-Goals

**Goals:**
- Build a reproducible RAG pipeline covering 20+ public documents.
- Use 100% local embedding model without requiring API keys.
- Accurately process tables and structural sections (articles/rules) into meaningful textual chunks.
- Generate a standalone `skill.md` summarizing the domain for AI agents.

**Non-Goals:**
- Productionize or host this as a web service.
- Automate scraping of the source documents (they can be manually curated and downloaded initially).
- Implement multi-agent or complex multi-step reasoning capabilities.

## Decisions
1. **Embedding**: `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) will be used to ensure local, API-key free embedding generation with strong multilingual (Traditional Chinese) capability.
2. **Vector Store**: `ChromaDB` (local persistent mode) is chosen over `pgvector` to avoid Docker dependency overhead for a personal CLI tool.
3. **LLM Interface**: `LiteLLM` will interface with `gemini-2.5-flash` primarily. This decouples the core logic from specific model providers.
4. **Chunking Strategy**: Rather than standard Langchain recursive character splitting, custom regex-based splitting on Markdown/PDF converted text will isolate articles (第X條) and structurally flatten tables into simple declarative sentences to preserve meaning.

## Risks / Trade-offs
- [Risk] Table extraction from PDF is often lossy. → Mitigation: Convert fee rate tables manually to structured CSV or use an intelligent parser (e.g. LlamaParse or unstructured) and convert to natural language sentences before chunking.
- [Risk] `paraphrase-multilingual-MiniLM-L12-v2` has a limited context window (512 tokens). → Mitigation: Keep chunks tight, splitting strictly by paragraph or sub-article.
- [Risk] Hallucinating jurisdiction (e.g. mixing EU and TW rules). → Mitigation: Enforce strict metadata filtering (e.g. `jurisdiction: TW`) and hardcode context framing into the RAG system prompt.
