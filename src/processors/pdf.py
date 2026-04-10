import logging
from pathlib import Path
from typing import Union

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from .base import DocumentProcessor
from .factory import ProcessorFactory

logger = logging.getLogger(__name__)

class PDFProcessor(DocumentProcessor):
    """Processor for extracting text and tables from PDF documents."""

    def extract_text(self, file_path: Union[str, Path]) -> str:
        if pdfplumber is None or fitz is None:
            raise ImportError("Please install 'pdfplumber' and 'pymupdf' to use PDFProcessor.")

        file_path_str = str(file_path)
        extracted_text = []

        try:
            with pdfplumber.open(file_path_str) as pdf:
                for page in pdf.pages:
                    # Extract standard text
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
                    
                    # Extract tables naturally
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            # Combine valid cells into a row layout
                            row_text = " | ".join(str(cell).strip() for cell in row if cell)
                            if row_text:
                                extracted_text.append(row_text)
                                
            full_text = "\n".join(extracted_text)
            if not full_text.strip():
                raise ValueError("pdfplumber extracted empty content.")
                
            return full_text

        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {file_path_str}: {e}. Falling back to pymupdf.")
            return self._fallback_extract_text(file_path_str)

    def _fallback_extract_text(self, file_path_str: str) -> str:
        extracted_text = []
        with fitz.open(file_path_str) as doc:
            for page in doc:
                text = page.get_text()
                if text:
                    extracted_text.append(text)
        return "\n".join(extracted_text)

# Register automatically upon import
ProcessorFactory.register(".pdf", PDFProcessor)
