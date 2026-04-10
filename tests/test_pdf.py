import os
import pytest
from unittest.mock import patch

# For TDD, it will fail to import until implemented
try:
    from src.processors.pdf import PDFProcessor
except ImportError:
    PDFProcessor = None

# We use a real PDF from the data/raw folder
REAL_PDF_PATH = "data/raw/碳費收費辦法總說明及逐條說明.pdf"

@pytest.mark.skipif(not os.path.exists(REAL_PDF_PATH), reason="Real PDF data not found")
def test_pdf_processor_real_success():
    """Test PDFProcessor using a real PDF file, with the standard pdfplumber logic."""
    assert PDFProcessor is not None, "PDFProcessor should be defined in src.processors.pdf"
    
    processor = PDFProcessor()
    text = processor.extract_text(REAL_PDF_PATH)
    
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 100
    assert "溫室氣體" in text  
    assert "費" in text  


@pytest.mark.skipif(not os.path.exists(REAL_PDF_PATH), reason="Real PDF data not found")
@patch("src.processors.pdf.pdfplumber.open") if PDFProcessor is not None else patch("builtins.open")
def test_pdf_processor_real_fallback(mock_pdfplumber_open):
    """Test PDFProcessor fallback to pymupdf when pdfplumber fails."""
    assert PDFProcessor is not None, "PDFProcessor should be defined in src.processors.pdf"
    
    # Force pdfplumber to fail so it triggers the fitz fallback
    mock_pdfplumber_open.side_effect = Exception("Simulated pdfplumber crash")
    
    processor = PDFProcessor()
    text = processor.extract_text(REAL_PDF_PATH)
    
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 100
    assert "溫室氣體" in text
    assert "費" in text
