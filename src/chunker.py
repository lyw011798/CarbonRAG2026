import re
from typing import List, Dict, Any

class ChunkStrategy:
    """
    Splits document text into chunks based on Taiwan legal article legislative structures (e.g., 第X條)
    and attaches relevant context and metadata.
    """
    
    def __init__(self, max_chunk_size: int = 1500):
        self.max_chunk_size = max_chunk_size
        
        # Regex to match Taiwan legal article boundaries: e.g., 第一條, 第十二條之五 etc.
        # It looks for "第" followed by Chinese numerals, and "條".
        self.article_pattern = re.compile(r'^\s*(第[一二三四五六七八九十百千]+條(?:之[一二三四五六七八九十]+)?)(.*)', re.MULTILINE)

    def split_text(self, text: str, initial_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits text into chunks preserving the article headers.
        """
        if initial_metadata is None:
            initial_metadata = {}
            
        chunks = []
        
        # Find all article headers
        matches = list(self.article_pattern.finditer(text))
        
        if not matches:
            # If no legal structure is found, do standard paragraph-based chunking
            return self._basic_sub_chunk(text, "General", initial_metadata)
            
        # Handle preamble text before the first article
        if matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                chunks.extend(self._basic_sub_chunk(preamble, "Preamble", initial_metadata))
            
        # Extract chunks between articles
        for i, match in enumerate(matches):
            article_header = match.group(1).strip()
            start_pos = match.start()
            
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            chunk_text = text[start_pos:end_pos].strip()
            
            # Sub-chunk if the article itself is too long
            sub_chunks = self._basic_sub_chunk(chunk_text, article_header, initial_metadata)
            chunks.extend(sub_chunks)
            
        return chunks

    def _basic_sub_chunk(self, text: str, header_context: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sub-chunks a string if it exceeds max size, while injecting the header context 
        at the start of each piece so RAG models retain context.
        """
        if len(text) <= self.max_chunk_size:
            # Re-inject header context if it's missing (helps with clean split arrays where header might be lost)
            # Actually, `text` inherently contains the header from the regex slice, but we prepend it if it's "General" or "Preamble".
            return [{"text": text, "metadata": {**metadata, "article": header_context}}]
            
        # Simple window split by paragraphs
        sub_chunks = []
        paragraphs = text.split('\n')
        
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > self.max_chunk_size and current_chunk:
                # Append context header to sub-chunks to preserve retrieval performance
                chunk_str = current_chunk.strip()
                if not chunk_str.startswith(header_context) and header_context not in ["General", "Preamble"]:
                    chunk_str = f"[{header_context}] {chunk_str}"
                    
                sub_chunks.append({
                    "text": chunk_str,
                    "metadata": {**metadata, "article": header_context}
                })
                current_chunk = paragraph + "\n"
            else:
                current_chunk += paragraph + "\n"
                
        if current_chunk.strip():
            chunk_str = current_chunk.strip()
            if not chunk_str.startswith(header_context) and header_context not in ["General", "Preamble"]:
                chunk_str = f"[{header_context}] {chunk_str}"
                
            sub_chunks.append({
                "text": chunk_str,
                "metadata": {**metadata, "article": header_context}
            })
            
        return sub_chunks
