import re
from pathlib import Path
from typing import Union

from .base import DocumentProcessor
from .factory import ProcessorFactory


class MarkdownProcessor(DocumentProcessor):
    """Processor for extracting plain text from Markdown files while preserving headings."""

    def extract_text(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from file.
        Strips markdown links, bold, italic, and code symbols, 
        but preserves the '#' heading syntax.
        """
        file_path_obj = Path(file_path)
        
        # Read the file gracefully handling unexpected characters
        with file_path_obj.open('r', encoding='utf-8', errors='replace') as f:
            text = f.read()

        # 1. Strip URLs from Links: [link](url) -> link
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # 2. Strip Bold (**text** -> text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # 3. Strip bold with underscores
        text = re.sub(r'__(.*?)__', r'\1', text)

        # 4. Strip Italics (*text* -> text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # 5. Strip italics with underscores (using \b to avoid breaking snake_case variables ideally, but we'll use a simple approach)
        text = re.sub(r'\b_(.*?)_\b', r'\1', text)

        # 6. Strip inline code (`code` -> code)
        text = re.sub(r'`(.*?)`', r'\1', text)

        return text

# Register processor dynamically
ProcessorFactory.register(".md", MarkdownProcessor)
