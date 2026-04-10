import pytest
from unittest.mock import Mock
from src.builder import SkillBuilder

class TestSkillBuilder:
    def test_skillbuilder_contains_defined_query_groups(self):
        """Verify SkillBuilder initializes with the predefined query groups."""
        mock_query = Mock()
        builder = SkillBuilder(query_engine=mock_query)
        assert hasattr(builder, "QUERY_GROUPS")
        assert len(builder.QUERY_GROUPS) >= 3  # Ensure we have our core categories
        
        # Check that we have a mix of mechanisms
        categories = list(builder.QUERY_GROUPS.keys())
        assert any("碳費" in cat for cat in categories)
        assert any("自主減量" in cat for cat in categories)

    def test_build_skill_content_generates_markdown(self):
        """Test the generation loop aggregates queries correctly."""
        # Arrange
        mock_query_engine = Mock()
        mock_query_engine.query.return_value = {
            "answer": "Mocked generated answer.",
            "sources": [{"filename": "doc.txt", "article": "Rule 1"}]
        }
        
        builder = SkillBuilder(query_engine=mock_query_engine)
        
        # Override groups for shorter test
        builder.QUERY_GROUPS = {
            "Test Category": ["What is XYZ?"]
        }
        
        # Act
        content = builder.build_skill_content(n_results=2, use_mock=False)
        
        # Assert
        assert "# Taiwan Carbon Market RAG" in content
        assert "## Test Category" in content
        assert "### Q: What is XYZ?" in content
        assert "**A:** Mocked generated answer." in content
        assert "*Citations:*" in content
        assert "`doc.txt -> Rule 1`" in content
        
        mock_query_engine.query.assert_called_once_with(question="What is XYZ?", n_results=2, use_mock=False)
