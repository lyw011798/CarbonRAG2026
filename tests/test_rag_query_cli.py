import sys
from unittest.mock import Mock, patch

import rag_query


def test_main_defaults_to_interactive_loop(monkeypatch):
    mock_store = Mock()
    mock_query_engine = Mock()

    with patch("src.store.VectorStore", return_value=mock_store) as mock_store_cls, \
         patch("src.query.RAGQuery", return_value=mock_query_engine) as mock_query_cls:
        interactive_loop = Mock()
        monkeypatch.setattr(rag_query, "interactive_loop", interactive_loop)
        monkeypatch.setattr(sys, "argv", ["rag_query.py", "--db-path", "/tmp/test-db"])

        rag_query.main()

    mock_store_cls.assert_called_once_with(db_path="/tmp/test-db")
    mock_query_cls.assert_called_once_with(vector_store=mock_store, model="gemini-2.5-flash")
    interactive_loop.assert_called_once_with(query_engine=mock_query_engine, n_results=5)


def test_main_runs_one_time_query(monkeypatch, capsys):
    mock_store = Mock()
    mock_query_engine = Mock()
    mock_query_engine.query.return_value = {
        "answer": "碳費一般費率為每噸300元。",
        "sources": [
            {
                "filename": "fee.txt",
                "section": "一般費率",
                "article": "一般費率",
                "score": 0.9123,
            }
        ],
    }

    with patch("src.store.VectorStore", return_value=mock_store) as mock_store_cls, \
         patch("src.query.RAGQuery", return_value=mock_query_engine) as mock_query_cls:
        interactive_loop = Mock()
        monkeypatch.setattr(rag_query, "interactive_loop", interactive_loop)
        monkeypatch.setattr(sys, "argv", [
            "rag_query.py",
            "--db-path", "/tmp/test-db",
            "--query", "碳費一般費率是多少？",
            "--top-k", "3",
            "--model", "gemini-2.5-flash",
        ])

        rag_query.main()

    mock_store_cls.assert_called_once_with(db_path="/tmp/test-db")
    mock_query_cls.assert_called_once_with(vector_store=mock_store, model="gemini-2.5-flash")
    mock_query_engine.query.assert_called_once_with(question="碳費一般費率是多少？", n_results=3)
    interactive_loop.assert_not_called()

    output = capsys.readouterr().out
    assert "Answer:" in output
    assert "碳費一般費率為每噸300元。" in output
    assert "Sources:" in output
    assert "[1] fee.txt  (section: 一般費率, score: 0.9123)" in output