import os
import pytest

# For TDD, it will fail to import until implemented
try:
    from src.processors.text import TextProcessor
except ImportError:
    TextProcessor = None

# We use real text files from the data/raw folder
RAW_TXT_1 = "data/raw/氣候變遷因應法.txt"
RAW_TXT_2 = "data/raw/臺灣碳權市場趨勢報告.txt"

@pytest.mark.skipif(not os.path.exists(RAW_TXT_1), reason="Real TXT data not found")
def test_text_processor_real_climate_change_act():
    """Test TextProcessor using the real 氣候變遷因應法 file."""
    assert TextProcessor is not None, "TextProcessor should be defined in src.processors.text"
    
    processor = TextProcessor()
    text = processor.extract_text(RAW_TXT_1)
    
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 100
    assert "氣候變遷" in text


@pytest.mark.skipif(not os.path.exists(RAW_TXT_2), reason="Real TXT data not found")
def test_text_processor_real_market_trends():
    """Test TextProcessor on the real 臺灣碳權市場趨勢報告 file (verifying robust encoding)."""
    assert TextProcessor is not None, "TextProcessor should be defined in src.processors.text"
    
    processor = TextProcessor()
    text = processor.extract_text(RAW_TXT_2)
    
    assert text is not None
    assert isinstance(text, str)
    assert len(text) > 100
    assert "碳權" in text
