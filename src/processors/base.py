import abc
from pathlib import Path

class DocumentProcessor(abc.ABC):
    """Abstract base class for document format processors.
    
    Each subclass is responsible for handling a specific document format,
    extracting its text, and applying initial sanitization specific to that format.
    """

    @abc.abstractmethod
    def extract_text(self, file_path: str | Path) -> str:
        """
        Extract and sanitize text from the given file.
        
        Args:
            file_path: Path to the document.
            
        Returns:
            Sanitized string representation of the document's text flow,
            ready for further parsing and chunking.
        """
        pass
