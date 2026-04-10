import re
from typing import List, Dict, Any, Optional, Tuple


class ChunkStrategy:
    """
    Multi-strategy document chunker that auto-detects document structure
    and splits text at semantically meaningful boundaries.
    
    Supported strategies (in priority order):
    1. Taiwan Legal Articles (第X條)
    2. EU Regulation Articles (Article X)
    3. Government Form Tables (表/附表)
    4. Numbered Sections (X.Y)
    5. Fallback paragraph chunking with overlap
    """
    
    def __init__(self, max_chunk_size: int = 2000, overlap_lines: int = 1):
        self.max_chunk_size = max_chunk_size
        self.overlap_lines = overlap_lines
        
        # Strategy 1: Taiwan legal article boundaries: e.g., 第一條, 第十二條之五
        self.legal_article_pattern = re.compile(
            r'^\s*(第[一二三四五六七八九十百千]+條(?:之[一二三四五六七八九十]+)?)(.*)',
            re.MULTILINE
        )
        
        # Strategy 2: EU regulation article boundaries: e.g., Article 1, Article 26
        # Must be at the start of a line to distinguish from body references
        self.eu_article_pattern = re.compile(
            r'^(Article\s+\d+)\s*$',
            re.MULTILINE
        )
        
        # Strategy 3: Government form table headers: e.g., 表 C, 附表 G－A, 附表 C-A
        self.form_table_pattern = re.compile(
            r'^(附?表\s*[A-Z][^\n]*?)$',
            re.MULTILINE
        )
        
        # Strategy 4a: Numbered section headers: e.g., 1.1 背景, 2.3 結果
        self.numbered_section_pattern = re.compile(
            r'^(\d+\.\d+)\s+(\S[^\n]*)',
            re.MULTILINE
        )
        
        # Strategy 4b: Chinese numeral outline headers: e.g., 一、法源依據, 十二、施行日
        self.chinese_outline_pattern = re.compile(
            r'^([一二三四五六七八九十]+)、(\S[^\n]*)',
            re.MULTILINE
        )
    
    def _detect_strategy(self, text: str) -> str:
        """
        Detect the best splitting strategy based on content patterns.
        Returns a strategy name string. Priority order matters.
        """
        legal_matches = list(self.legal_article_pattern.finditer(text))
        eu_matches = list(self.eu_article_pattern.finditer(text))
        form_matches = list(self.form_table_pattern.finditer(text))
        section_matches = list(self.numbered_section_pattern.finditer(text))
        outline_matches = list(self.chinese_outline_pattern.finditer(text))
        
        # Priority 1: Taiwan legal articles (most specific)
        if len(legal_matches) >= 1:
            return 'legal'
        
        # Priority 2: EU regulation articles
        if len(eu_matches) >= 1:
            return 'eu_regulation'
        
        # Priority 3: Government form tables
        if len(form_matches) >= 1:
            return 'form_table'
        
        # Priority 4: Numbered sections or Chinese numeral outlines
        if len(section_matches) >= 2:
            return 'numbered_section'
        if len(outline_matches) >= 2:
            return 'chinese_outline'
        
        return 'fallback'
    
    def split_text(self, text: str, initial_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits text into chunks using auto-detected strategy.
        """
        if initial_metadata is None:
            initial_metadata = {}
        
        # Handle empty/whitespace input
        if not text or not text.strip():
            return []
        
        strategy = self._detect_strategy(text)
        
        if strategy == 'legal':
            return self._split_legal(text, initial_metadata)
        elif strategy == 'eu_regulation':
            return self._split_eu_regulation(text, initial_metadata)
        elif strategy == 'form_table':
            return self._split_form_table(text, initial_metadata)
        elif strategy == 'numbered_section':
            return self._split_numbered_section(text, initial_metadata)
        elif strategy == 'chinese_outline':
            return self._split_chinese_outline(text, initial_metadata)
        else:
            return self._split_fallback(text, initial_metadata)
    
    # ──────────────────────────────────────────
    # Strategy 1: Taiwan Legal Articles
    # ──────────────────────────────────────────
    
    def _split_legal(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits text on Taiwan legal article boundaries (第X條)."""
        chunks = []
        matches = list(self.legal_article_pattern.finditer(text))
        
        # Handle preamble before first article
        if matches and matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                chunks.extend(self._basic_sub_chunk(preamble, "Preamble", metadata))
        
        # Extract chunks between articles
        for i, match in enumerate(matches):
            article_header = match.group(1).strip()
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start_pos:end_pos].strip()
            chunks.extend(self._basic_sub_chunk(chunk_text, article_header, metadata))
        
        return chunks
    
    # ──────────────────────────────────────────
    # Strategy 2: EU Regulation Articles
    # ──────────────────────────────────────────
    
    def _split_eu_regulation(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits text on EU regulation article boundaries (Article X)."""
        chunks = []
        matches = list(self.eu_article_pattern.finditer(text))
        
        # Handle preamble before first article
        if matches and matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                chunks.extend(self._basic_sub_chunk(preamble, "Preamble", metadata))
        
        # Extract chunks between articles
        for i, match in enumerate(matches):
            article_header = match.group(1).strip()
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start_pos:end_pos].strip()
            chunks.extend(self._basic_sub_chunk(chunk_text, article_header, metadata))
        
        return chunks
    
    # ──────────────────────────────────────────
    # Strategy 3: Government Form Tables
    # ──────────────────────────────────────────
    
    def _split_form_table(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits text on government form table headers (表 X / 附表 X-Y)."""
        chunks = []
        matches = list(self.form_table_pattern.finditer(text))
        
        # Handle preamble before first table
        if matches and matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                chunks.extend(self._basic_sub_chunk(preamble, "Preamble", metadata))
        
        # Extract chunks between table headers
        for i, match in enumerate(matches):
            table_header = match.group(1).strip()
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start_pos:end_pos].strip()
            chunks.extend(self._basic_sub_chunk(chunk_text, table_header, metadata))
        
        return chunks
    
    # ──────────────────────────────────────────
    # Strategy 4: Numbered Sections
    # ──────────────────────────────────────────
    
    def _split_numbered_section(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits text on numbered section headers (e.g. 1.1, 2.3)."""
        chunks = []
        matches = list(self.numbered_section_pattern.finditer(text))
        
        # Handle preamble before first section
        if matches and matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                chunks.extend(self._basic_sub_chunk(preamble, "Preamble", metadata))
        
        # Extract chunks between sections
        for i, match in enumerate(matches):
            section_num = match.group(1).strip()
            section_title = match.group(2).strip()
            section_header = f"{section_num} {section_title}"
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start_pos:end_pos].strip()
            chunks.extend(self._basic_sub_chunk(chunk_text, section_header, metadata))
        
        return chunks
    
    # ──────────────────────────────────────────
    # Strategy 4b: Chinese Numeral Outlines
    # ──────────────────────────────────────────
    
    def _split_chinese_outline(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits text on Chinese numeral outline headers (e.g. 一、法源依據)."""
        chunks = []
        matches = list(self.chinese_outline_pattern.finditer(text))
        
        # Handle preamble before first outline item
        if matches and matches[0].start() > 0:
            preamble = text[:matches[0].start()].strip()
            if preamble:
                chunks.extend(self._basic_sub_chunk(preamble, "Preamble", metadata))
        
        # Extract chunks between outline items
        for i, match in enumerate(matches):
            outline_num = match.group(1).strip()
            outline_title = match.group(2).strip()
            outline_header = f"{outline_num}、{outline_title}"
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chunk_text = text[start_pos:end_pos].strip()
            chunks.extend(self._basic_sub_chunk(chunk_text, outline_header, metadata))
        
        return chunks
    
    # ──────────────────────────────────────────
    # Strategy 5: Fallback with overlap
    # ──────────────────────────────────────────
    
    def _split_fallback(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Paragraph-based chunking with overlap for context preservation."""
        return self._basic_sub_chunk(text, "General", metadata)
    
    # ──────────────────────────────────────────
    # Shared: Sub-chunking logic
    # ──────────────────────────────────────────
    
    def _basic_sub_chunk(self, text: str, header_context: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Sub-chunks a string if it exceeds max size, while injecting the header context 
        at the start of each piece so RAG models retain context.
        Includes overlap between chunks for better retrieval.
        """
        if len(text) <= self.max_chunk_size:
            return [{"text": text, "metadata": {**metadata, "article": header_context}}]
            
        # Split by paragraphs (lines)
        sub_chunks = []
        paragraphs = text.split('\n')
        
        current_chunk_lines = []
        current_size = 0
        
        for paragraph in paragraphs:
            line_len = len(paragraph) + 1  # +1 for newline
            
            if current_size + line_len > self.max_chunk_size and current_chunk_lines:
                # Emit current chunk
                chunk_str = '\n'.join(current_chunk_lines).strip()
                if not chunk_str.startswith(header_context) and header_context not in ["General", "Preamble"]:
                    chunk_str = f"[{header_context}] {chunk_str}"
                    
                sub_chunks.append({
                    "text": chunk_str,
                    "metadata": {**metadata, "article": header_context}
                })
                
                # Keep last N lines as overlap for next chunk
                overlap = current_chunk_lines[-self.overlap_lines:]
                current_chunk_lines = overlap + [paragraph]
                current_size = sum(len(l) + 1 for l in current_chunk_lines)
            else:
                current_chunk_lines.append(paragraph)
                current_size += line_len
                
        # Emit final chunk
        if current_chunk_lines:
            chunk_str = '\n'.join(current_chunk_lines).strip()
            if chunk_str:
                if not chunk_str.startswith(header_context) and header_context not in ["General", "Preamble"]:
                    chunk_str = f"[{header_context}] {chunk_str}"
                    
                sub_chunks.append({
                    "text": chunk_str,
                    "metadata": {**metadata, "article": header_context}
                })
            
        return sub_chunks
