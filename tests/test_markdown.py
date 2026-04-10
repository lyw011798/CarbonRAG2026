import pytest
from pathlib import Path

# For TDD, it will fail to import until implemented
try:
    from src.processors.markdown import MarkdownProcessor
except ImportError:
    MarkdownProcessor = None

def test_markdown_processor_preserves_headings(tmp_path: Path):
    """
    Test that MarkdownProcessor extracts text, strips syntax (like bold, links),
    but preserves the `# Heading` hierarchy.
    """
    assert MarkdownProcessor is not None, "MarkdownProcessor should be defined in src.processors.markdown"
    
    test_file = tmp_path / "test.md"
    md_content = """# First Degree Heading
    
This is a **bold** and *italic* text.

## Second Degree Heading

Check out this [link to Taiwan Carbon Exchange](https://www.tcx.com.tw).
"""
    test_file.write_text(md_content, encoding="utf-8")
    
    processor = MarkdownProcessor()
    extracted = processor.extract_text(test_file)
    
    assert extracted is not None
    
    # 1. Headings must be preserved
    assert "# First Degree Heading" in extracted
    assert "## Second Degree Heading" in extracted
    
    # 2. Text should be preserved, but syntax should be stripped
    assert "bold" in extracted
    assert "**bold**" not in extracted
    
    assert "italic" in extracted
    assert "*italic*" not in extracted
    
    # Link text preserved, URL stripped
    assert "link to Taiwan Carbon Exchange" in extracted
    assert "(https://www.tcx.com.tw)" not in extracted
    assert "[link" not in extracted
