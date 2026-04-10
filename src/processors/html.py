import logging
from pathlib import Path
from typing import Union
import warnings



try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .base import DocumentProcessor
from .factory import ProcessorFactory

logger = logging.getLogger(__name__)


class HTMLProcessor(DocumentProcessor):
    """Processor for extracting clean, readable text from HTML documents while stripping noise."""

    def extract_text(self, file_path: Union[str, Path]) -> str:
        """
        Extract the visible text from the HTML document.
        Removes noisy semantic tags like <nav>, <style>, <script>, <footer>, etc.
        """

        file_path_obj = Path(file_path)
        raw_bytes = file_path_obj.read_bytes()
        
        try:
            html_content = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            logger.warning(f"UTF-8 strict decoding failed for {file_path_obj.name}, falling back to replacement chars.")
            html_content = raw_bytes.decode('utf-8', errors='replace')

        from bs4 import XMLParsedAsHTMLWarning
        # Use lxml for fast, resilient parsing
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
            soup = BeautifulSoup(html_content, "lxml")

        # Decompose elements that generally don't contain regulatory body text
        for element in soup(["script", "style", "head", "title", "meta", "noscript", "nav", "footer"]):
            element.decompose()

        # Extract the pure text, breaking at logical structural elements
        text = soup.get_text(separator='\n', strip=True)

        return text

# Register dynamically
ProcessorFactory.register(".html", HTMLProcessor)
