import os
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional

class VectorStore:
    """
    Encapsulates ChromaDB and sentence-transformers to provide a localized
    vector storage and retrieval system for Taiwan regulatory documents.
    """
    
    def __init__(
        self, 
        db_path: str = "./db/chroma", 
        collection_name: str = "taiwan_carbon_market",
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ):
        # Initialize embedding model locally
        self.model = SentenceTransformer(model_name)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """
        Embeds and adds document chunks to the collection.
        
        Args:
            chunks: A list of dictionaries, each containing:
                - text: The chunk content
                - metadata: Dictionary of associated metadata
        """
        if not chunks:
            return

        import hashlib
        
        # Calculate deterministic IDs and deduplicate internally
        seen_ids = set()
        deduped_chunks = []
        deduped_ids = []
        
        for c in chunks:
            content_hash = hashlib.sha256(c["text"].encode("utf-8")).hexdigest()
            if content_hash not in seen_ids:
                seen_ids.add(content_hash)
                deduped_chunks.append(c)
                deduped_ids.append(content_hash)
                
        if not deduped_ids:
            return
            
        # Check which IDs already exist
        existing = self.collection.get(ids=deduped_ids)
        existing_ids = set(existing['ids']) if existing and 'ids' in existing else set()
        
        # Filter chunks that need processing
        new_texts = []
        new_metadatas = []
        new_ids = []
        
        for i, chunk in enumerate(deduped_chunks):
            if deduped_ids[i] not in existing_ids:
                new_texts.append(chunk["text"])
                new_metadatas.append(chunk["metadata"])
                new_ids.append(deduped_ids[i])

                
        if not new_texts:
            return

        # Calculate embeddings locally
        embeddings = self.model.encode(new_texts).tolist()
        
        # Upsert into ChromaDB
        self.collection.add(
            documents=new_texts,
            embeddings=embeddings,
            metadatas=new_metadatas,
            ids=new_ids
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs semantic search for the given query text.
        """
        query_embedding = self.model.encode([query_text]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results into a cleaner list
        formatted_results = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
                
        return formatted_results

    def reset_collection(self):
        """
        Clears all items in the current collection.
        """
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)
