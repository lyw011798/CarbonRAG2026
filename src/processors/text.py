import logging
from pathlib import Path
from typing import Union

from .base import DocumentProcessor
from .factory import ProcessorFactory

logger = logging.getLogger(__name__)

class TextProcessor(DocumentProcessor):
    """Processor for extracting plain text from standard .txt files."""

    def extract_text(self, file_path: Union[str, Path]) -> str:
        """
        Extract raw text directly, utilizing a fallback mechanism for
        traditional Chinese BIG5 encoding if UTF-8 fails.
        """
        file_path_obj = Path(file_path)
        raw_bytes = file_path_obj.read_bytes()
        
        # 1. Standard UTF-8 decoding
        try:
            return raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            pass
            
        # 2. Legacy BIG5 decoding (common for Taiwan government documents)
        try:
            logger.info(f"UTF-8 decoding failed for {file_path_obj.name}, attempting BIG5.")
            return raw_bytes.decode('big5')
        except UnicodeDecodeError:
            pass
            
        # 3. Fallback replacement
        logger.warning(f"Strict decoding failed for {file_path_obj.name}. Falling back to replacement.")
        return raw_bytes.decode('utf-8', errors='replace')

# Register processor
ProcessorFactory.register(".txt", TextProcessor)
