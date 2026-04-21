import os
import uuid
import pickle
import jieba
import chromadb
from rank_bm25 import BM25Okapi
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
        model_name: str = "intfloat/multilingual-e5-small"
    ):
        self.db_path = db_path
        self.model_name = model_name
        # Initialize embedding model locally
        self.model = SentenceTransformer(model_name)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.bm25 = None
        self.bm25_ids = []
        self.bm25_metadatas = []
        self.bm25_texts = []
        self.bm25_tokenized = []
        self._load_bm25()

    def _load_bm25(self):
        bm25_path = os.path.join(self.db_path, "bm25.pkl")
        if os.path.exists(bm25_path):
            with open(bm25_path, 'rb') as f:
                data = pickle.load(f)
                self.bm25_ids = data.get('ids', [])
                self.bm25_metadatas = data.get('metadatas', [])
                self.bm25_texts = data.get('texts', [])
                self.bm25_tokenized = data.get('tokenized', [])
            if self.bm25_tokenized:
                self.bm25 = BM25Okapi(self.bm25_tokenized)
                
    def _save_bm25(self):
        os.makedirs(self.db_path, exist_ok=True)
        bm25_path = os.path.join(self.db_path, "bm25.pkl")
        with open(bm25_path, 'wb') as f:
            pickle.dump({
                'ids': self.bm25_ids,
                'metadatas': self.bm25_metadatas,
                'texts': self.bm25_texts,
                'tokenized': self.bm25_tokenized
            }, f)
        
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
        if "e5" in self.model_name.lower():
            texts_to_embed = ["passage: " + t for t in new_texts]
        else:
            texts_to_embed = new_texts
            
        embeddings = self.model.encode(texts_to_embed).tolist()
        
        # Upsert into ChromaDB
        self.collection.add(
            documents=new_texts,
            embeddings=embeddings,
            metadatas=new_metadatas,
            ids=new_ids
        )
        
        # Update BM25
        self.bm25_texts.extend(new_texts)
        self.bm25_metadatas.extend(new_metadatas)
        self.bm25_ids.extend(new_ids)
        new_tokenized = [list(jieba.cut(doc)) for doc in new_texts]
        self.bm25_tokenized.extend(new_tokenized)
        
        if self.bm25_tokenized:
            self.bm25 = BM25Okapi(self.bm25_tokenized)
        self._save_bm25()

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs semantic search for the given query text.
        """
        if "e5" in self.model_name.lower():
            query_to_embed = "query: " + query_text
        else:
            query_to_embed = query_text
            
        query_embedding = self.model.encode([query_to_embed]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results into a cleaner list
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i] if 'ids' in results else None,
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
                
        return formatted_results

    def query_bm25(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top K chunks using BM25 sparse token scoring.
        """
        if not self.bm25:
            return []
            
        tokenized_query = list(jieba.cut(query_text))
        scores = self.bm25.get_scores(tokenized_query)
        
        top_n = min(n_results, len(scores))
        if top_n == 0:
            return []
            
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
        
        formatted_results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score <= 0:
                continue
            formatted_results.append({
                "id": self.bm25_ids[idx],
                "text": self.bm25_texts[idx],
                "metadata": self.bm25_metadatas[idx],
                "bm25_score": score
            })
            
        return formatted_results

    def reset_collection(self):
        """
        Clears all items in the current collection.
        """
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)
        
        # Reset BM25
        self.bm25 = None
        self.bm25_ids = []
        self.bm25_metadatas = []
        self.bm25_texts = []
        self.bm25_tokenized = []
        bm25_path = os.path.join(self.db_path, "bm25.pkl")
        if os.path.exists(bm25_path):
            os.remove(bm25_path)
