import os
import pytest

# For TDD, it will fail to import until implemented
try:
    from src.processors.html import HTMLProcessor
except ImportError:
    HTMLProcessor = None

REAL_HTML_1 = "data/raw/CELEX_32023R0956_EN_TXT.html"
REAL_HTML_2 = "data/raw/OJ_L_202502083_EN_TXT.html"

@pytest.mark.skipif(not os.path.exists(REAL_HTML_1), reason="Real HTML data not found")
def test_html_processor_real_celex():
    """Test HTMLProcessor using the genuine CELEX EU carbon regulation HTML document."""
    assert HTMLProcessor is not None, "HTMLProcessor should be defined in src.processors.html"
    
    processor = HTMLProcessor()
    text = processor.extract_text(REAL_HTML_1)
    
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 1000
    # Sanity checks for EU Regulation text
    assert "The Commission, in consultation with relevant stakeholders, shall collect the information necessary with a view to extending the scope of this Regulation as indicated in and pursuant to paragraph 2, point (a), and to developing methods of calculating embedded emissions based on environmental footprint methods." in text
    assert "<html" not in text  # Ensure tags are actually stripped out
    assert "<div" not in text

@pytest.mark.skipif(not os.path.exists(REAL_HTML_2), reason="Real HTML data not found")
def test_html_processor_real_oj():
    """Test HTMLProcessor using the genuine OJ HTML document."""
    assert HTMLProcessor is not None, "HTMLProcessor should be defined in src.processors.html"
    
    processor = HTMLProcessor()
    text = processor.extract_text(REAL_HTML_2)
    
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 1000
    assert "After consulting the Committee of the Regions" in text
    assert "<html" not in text  # Ensure tags are actually stripped out
    assert "<style" not in text
