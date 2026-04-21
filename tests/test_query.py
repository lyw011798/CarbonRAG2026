import os
import pytest
from unittest.mock import Mock, patch
from dotenv import load_dotenv
from src.query import RAGQuery

load_dotenv()

class TestRAGQuery:
    def test_rag_query_initialization(self):
        """Test successful initialization with custom model name."""
        mock_store = Mock()
        query_engine = RAGQuery(vector_store=mock_store, model="test-model-123")
        assert query_engine.model == "test-model-123"

    def test_rag_query_generates_answer_with_mock(self):
        """Test that use_mock bypasses the API completely and returns simulated answer."""
        # Arrange
        mock_store = Mock()
        mock_store.query.return_value = [
            {"text": "碳費徵收費率為一般費率300元", "metadata": {"article": "公告事項", "filename": "fee.txt"}}
        ]
        mock_store.query_bm25 = Mock(return_value=[])
        query_engine = RAGQuery(vector_store=mock_store)
        
        # Act
        result = query_engine.query("碳費一般費率是多少？", use_mock=True)
        
        # Assert
        assert "answer" in result
        assert "sources" in result
        assert "Mock" in result["answer"]
        assert "碳費一般費率是多少" in result["answer"]
        
        assert len(result["sources"]) == 1
        assert result["sources"][0]["article"] == "公告事項"
        assert result["sources"][0]["filename"] == "fee.txt"
        assert result["sources"][0]["section"] == "公告事項"
        assert "score" in result["sources"][0]
        
        mock_store.query.assert_called_once_with("碳費一般費率是多少？", n_results=10)

    @patch("src.query.completion")
    def test_rag_query_constructs_prompt_correctly(self, mock_completion):
        """Test that the system prompt and context are properly constructed to litellm."""
        # Arrange
        mock_store = Mock()
        mock_store.query.return_value = [
            {"id": "doc1", "text": "台灣碳費一般費率為300元。", "metadata": {"article": "一般費率", "filename": "碳費公告"}},
            {"id": "doc2", "text": "優惠費率A為50元。", "metadata": {"article": "優惠費率", "filename": "碳費公告"}}
        ]
        mock_store.query_bm25 = Mock(return_value=[])
        
        mock_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="API Answer based on context."))]
        )
        
        query_engine = RAGQuery(vector_store=mock_store, model="gemini/gemini-pro")
        
        # Act
        result = query_engine.query("碳費是多少？", n_results=2)
        
        # Assert
        assert result["answer"] == "API Answer based on context."
        assert len(result["sources"]) == 2
        assert result["sources"][0]["article"] == "一般費率"
        assert result["sources"][1]["article"] == "優惠費率"
        
        # Verify the prompt construction
        mock_completion.assert_called_once()
        call_kwargs = mock_completion.call_args.kwargs
        assert call_kwargs["model"] == "gemini/gemini-pro"
        
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        
        # System prompt should include Taiwan context, same-language behavior, and citation guidance
        sys_prompt = messages[0]["content"].lower()
        assert "taiwan" in sys_prompt or "台灣" in sys_prompt
        assert "same language" in sys_prompt or "相同語言" in sys_prompt
        assert "[1][2]" in messages[1]["content"]
        
        # Check that context chunks and query are included in the user message
        user_msg = messages[1]["content"]
        assert "[1] 碳費公告 (section: 一般費率" in user_msg
        assert "[2] 碳費公告 (section: 優惠費率" in user_msg
        assert "台灣碳費一般費率為300元。" in user_msg
        assert "優惠費率A為50元。" in user_msg
        assert "碳費是多少？" in user_msg

    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not found in environment.")
    def test_rag_query_real_api_integration(self):
        """Integration test using the real Gemini API via Litellm."""
        # Arrange
        mock_store = Mock()
        mock_store.query.return_value = [
            {"id": "1", "text": "台灣的碳費一般費率訂為每公噸二氧化碳當量300元新台幣。", "metadata": {"article": "一般費率", "filename": "測試文件.txt"}}
        ]
        mock_store.query_bm25 = Mock(return_value=[])
        
        query_engine = RAGQuery(vector_store=mock_store, model="gemini/gemini-2.5-flash")
        
        # Act
        result = query_engine.query("請問台灣碳費的一般費率是多少？", n_results=1)
        
        # Assert
        assert "answer" in result
        assert "sources" in result
        
        # The LLM should extract "300" from the context
        assert "300" in result["answer"]
        assert "新台幣" in result["answer"] or "元" in result["answer"]
        
        assert len(result["sources"]) == 1
        assert result["sources"][0]["filename"] == "測試文件.txt"
