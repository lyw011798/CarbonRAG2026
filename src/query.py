from litellm import completion
from typing import List, Dict, Any

class RAGQuery:
    """
    Manages querying the VectorStore and submitting Context-Augmented Prompts 
    to an LLM via LiteLLM.
    """
    
    def __init__(self, vector_store, model: str = "gemini/gemini-2.5-flash"):
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
            "Answer the user's question accurately and thoroughly based strictly on the provided context. "
            "If the answer is not contained in the context, clearly summarize what is provided "
            "and state that the complete answer cannot be determined from the available context. "
            "Do not hallucinate any information. "
            "Always respond in Traditional Chinese (繁體中文)."
        )

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
                "sources": [{"filename": str, "article": str}, ...]
            }
        """
        # 1. Retrieve chunks
        results = self.vector_store.query(question, n_results=n_results)
        
        # 2. Build context string and extract sources
        context_parts = []
        sources = []
        seen_sources = set()
        
        for res in results:
            text = res.get('text', '')
            meta = res.get('metadata', {})
            article = meta.get('article', 'Unknown Article')
            filename = meta.get('filename', 'Unknown File')
            
            source_key = f"{filename}::{article}"
            if source_key not in seen_sources:
                sources.append({"filename": filename, "article": article})
                seen_sources.add(source_key)
                
            context_parts.append(f"Source: {filename} [{article}]\n{text}")
            
        context_text = "\n\n---\n\n".join(context_parts)
        
        # If no results found, we can still proceed, but the LLM will reply based on empty context
        if not context_parts:
            context_text = "No relevant context found."
            
        # 3. Construct messages
        user_prompt = f"Context Information:\n{context_text}\n\nQuestion:\n{question}"
        
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
