from litellm import completion
from typing import List, Dict, Any

class RAGQuery:
    """
    Manages querying the VectorStore and submitting Context-Augmented Prompts 
    to an LLM via LiteLLM.
    """
    
    def __init__(self, vector_store, model: str = "gemini-2.5-flash"):
        """
        Initialize the RAGQuery engine.
        
        Args:
            vector_store: An initialized VectorStore instance.
            model: The LiteLLM compatible model string. Defaults to Gemini 2.5 Flash.
        """
        self.vector_store = vector_store
        self.model = model
        
        self.system_prompt = (
            "You are a professional AI assistant specialized in Taiwan's regulatory guidelines, "
            "carbon market policies, greenhouse gas inventories, and related subjects. "
            "Answer the user's question in the same language as the question, based strictly on the provided context. "
            "If the answer is not contained in the context, clearly summarize what is provided "
            "and state that the complete answer cannot be determined from the available context. "
            "Do not hallucinate any information. "
            "When you use retrieved context, cite supporting sources with [1][2] notation."
        )

    @staticmethod
    def _format_score(distance: Any) -> Any:
        if distance is None:
            return None

        try:
            score = 1 - float(distance)
        except (TypeError, ValueError):
            return None

        return round(score, 4)

    def query(self, question: str, n_results: int = 5, use_mock: bool = False) -> Dict[str, Any]:
        """
        Retrieves context from VectorStore and queries the LLM.
        
        Args:
            question: The user's query.
            n_results: Number of chunks to retrieve from the vector store.
            use_mock: If True, bypasses the LLM API and returns a mock string.
            
        Returns:
            A dictionary containing the generated answer and a list of sources:
            {
                "answer": str,
                "sources": [{"filename": str, "section": str, "article": str, "score": float}, ...]
            }
        """
        # 1. Retrieve chunks via Dual Retrieval & Reciprocal Rank Fusion (RRF)
        dense_results = self.vector_store.query(question, n_results=n_results * 2)
        sparse_results = []
        if hasattr(self.vector_store, 'query_bm25'):
            sparse_results = self.vector_store.query_bm25(question, n_results=n_results * 2)
            
        combined_scores = {}
        items = {}
        
        # RRF k constant 
        rrf_k = 60
        
        for rank, item in enumerate(dense_results, start=1):
            doc_id = item.get('id', str(rank))
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (1.0 / (rrf_k + rank))
            items[doc_id] = item
            
        for rank, item in enumerate(sparse_results, start=1):
            doc_id = item.get('id', str(rank))
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (1.0 / (rrf_k + rank))
            items[doc_id] = item
            
        sorted_ids = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)
        results = [items[doc_id] for doc_id in sorted_ids[:n_results]]
        
        for doc_id in sorted_ids[:n_results]:
            items[doc_id]['_rrf_score'] = combined_scores[doc_id]
        
        # 2. Build context string and extract sources
        context_parts = []
        sources = []
        
        for index, res in enumerate(results, start=1):
            text = res.get('text', '')
            meta = res.get('metadata', {})
            section = meta.get('section', meta.get('article', 'Unknown Section'))
            article = meta.get('article', section)
            filename = meta.get('filename', 'Unknown File')
            
            if '_rrf_score' in res:
                score = round(res['_rrf_score'], 5)
            elif 'distance' in res:
                score = self._format_score(res.get('distance'))
            else:
                score = round(res.get('bm25_score', 0), 4)
            
            sources.append({
                "filename": filename,
                "section": section,
                "article": article,
                "score": score,
            })

            score_text = score if score is not None else "n/a"
            context_parts.append(
                f"[{index}] {filename} (section: {section}, score: {score_text})\n{text}"
            )
            
        context_text = "\n\n---\n\n".join(context_parts)
        
        # If no results found, we can still proceed, but the LLM will reply based on empty context
        if not context_parts:
            context_text = "No relevant context found."
            
        # 3. Construct messages
        user_prompt = (
            "Context Information:\n"
            f"{context_text}\n\n"
            "Instructions:\n"
            "- Answer in the same language as the question.\n"
            "- Use only the provided context.\n"
            "- Cite supporting sources with [1][2] notation when relevant.\n\n"
            f"Question:\n{question}"
        )
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 4. Generate response
        if use_mock:
            return {
                "answer": f"[Mock Answer] Based on the context, here is a simulated response to: '{question}'",
                "sources": sources
            }
            
        response = completion(
            model=self.model,
            messages=messages
        )
        
        return {
            "answer": response.choices[0].message.content,
            "sources": sources
        }
