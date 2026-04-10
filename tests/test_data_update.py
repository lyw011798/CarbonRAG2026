"""
TDD tests for data_update.py — the CLI ingestion pipeline orchestrator.

Written BEFORE implementation. All tests follow Arrange-Act-Assert.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from data_update import run_ingestion_pipeline, discover_files


# ---------------------------------------------------------------------------
# discover_files
# ---------------------------------------------------------------------------

class TestDiscoverFiles:
    """Tests for the directory traversal and file discovery function."""

    def test_discover_finds_txt_files(self, tmp_path):
        """discover_files should return .txt files in the target directory."""
        # Arrange
        (tmp_path / "doc.txt").write_text("hello", encoding="utf-8")

        # Act
        files = discover_files(str(tmp_path))

        # Assert
        assert len(files) == 1
        assert files[0].endswith("doc.txt")

    def test_discover_finds_multiple_supported_formats(self, tmp_path):
        """discover_files should return all four supported formats."""
        # Arrange
        for ext in [".txt", ".md", ".html", ".pdf"]:
            (tmp_path / f"file{ext}").write_bytes(b"data")

        # Act
        files = discover_files(str(tmp_path))

        # Assert
        assert len(files) == 4
        extensions = {Path(f).suffix for f in files}
        assert extensions == {".txt", ".md", ".html", ".pdf"}

    def test_discover_ignores_unsupported_extensions(self, tmp_path):
        """discover_files should skip files with unsupported extensions."""
        # Arrange
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "data.csv").write_text("a,b", encoding="utf-8")
        (tmp_path / "valid.txt").write_text("ok", encoding="utf-8")

        # Act
        files = discover_files(str(tmp_path))

        # Assert
        assert len(files) == 1
        assert files[0].endswith("valid.txt")

    def test_discover_traverses_subdirectories(self, tmp_path):
        """discover_files should recurse into subdirectories."""
        # Arrange
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.txt").write_text("nested", encoding="utf-8")

        # Act
        files = discover_files(str(tmp_path))

        # Assert
        assert len(files) == 1
        assert "subdir" in files[0]

    def test_discover_returns_empty_for_empty_directory(self, tmp_path):
        """discover_files should return an empty list for an empty directory."""
        # Arrange — tmp_path is already empty

        # Act
        files = discover_files(str(tmp_path))

        # Assert
        assert files == []

    def test_discover_raises_on_nonexistent_path(self):
        """discover_files should raise FileNotFoundError for a missing directory."""
        # Arrange
        bad_path = "/nonexistent/path/does/not/exist"

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            discover_files(bad_path)


# ---------------------------------------------------------------------------
# run_ingestion_pipeline  (integration-style with mocks for heavy I/O)
# ---------------------------------------------------------------------------

class TestRunIngestionPipeline:
    """Tests for the full ingestion orchestration function."""

    @patch("data_update.VectorStore")
    def test_pipeline_processes_txt_file(self, MockVectorStore, tmp_path):
        """Pipeline should extract, chunk, and store a .txt file."""
        # Arrange
        txt_file = tmp_path / "law.txt"
        txt_file.write_text(
            "第一條 本法為碳交易管理之基本法。\n第二條 主管機關為環境部。",
            encoding="utf-8",
        )
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        mock_store.add_documents.assert_called_once()
        chunks_arg = mock_store.add_documents.call_args[0][0]
        assert len(chunks_arg) >= 2  # at least 2 articles
        assert stats["processed"] == 1
        assert stats["skipped"] == 0

    @patch("data_update.VectorStore")
    def test_pipeline_processes_md_file(self, MockVectorStore, tmp_path):
        """Pipeline should handle .md files via MarkdownProcessor."""
        # Arrange
        md_file = tmp_path / "rules.md"
        md_file.write_text(
            "# 碳費收費辦法\n\n第一條 本辦法依據氣候法制定。",
            encoding="utf-8",
        )
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        mock_store.add_documents.assert_called_once()
        assert stats["processed"] == 1

    @patch("data_update.VectorStore")
    def test_pipeline_skips_unsupported_files(self, MockVectorStore, tmp_path):
        """Pipeline should count unsupported files as skipped, not crash."""
        # Arrange
        (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        mock_store.add_documents.assert_not_called()
        assert stats["processed"] == 0
        assert stats["skipped"] == 0  # discover_files filters them out

    @patch("data_update.VectorStore")
    def test_pipeline_attaches_filename_metadata(self, MockVectorStore, tmp_path):
        """Each chunk's metadata must include the source filename."""
        # Arrange
        txt_file = tmp_path / "carbon_act.txt"
        txt_file.write_text("碳費徵收機制概述。", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        chunks_arg = mock_store.add_documents.call_args[0][0]
        for chunk in chunks_arg:
            assert "filename" in chunk["metadata"]
            assert chunk["metadata"]["filename"] == "carbon_act.txt"

    @patch("data_update.VectorStore")
    def test_pipeline_attaches_source_path_metadata(self, MockVectorStore, tmp_path):
        """Each chunk's metadata must include the full source path."""
        # Arrange
        txt_file = tmp_path / "info.txt"
        txt_file.write_text("一般資訊。", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        chunks_arg = mock_store.add_documents.call_args[0][0]
        for chunk in chunks_arg:
            assert "source" in chunk["metadata"]
            assert chunk["metadata"]["source"] == str(txt_file)

    @patch("data_update.VectorStore")
    def test_pipeline_returns_stats(self, MockVectorStore, tmp_path):
        """Pipeline should return a summary dict with processed/skipped/errors."""
        # Arrange
        (tmp_path / "a.txt").write_text("text a", encoding="utf-8")
        (tmp_path / "b.txt").write_text("text b", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        assert stats["processed"] == 2
        assert "errors" in stats

    @patch("data_update.VectorStore")
    def test_pipeline_handles_processor_errors_gracefully(self, MockVectorStore, tmp_path):
        """If a processor raises, pipeline should record the error and continue."""
        # Arrange — a corrupted PDF will fail extraction
        bad_pdf = tmp_path / "broken.pdf"
        bad_pdf.write_bytes(b"not a real pdf")
        good_txt = tmp_path / "ok.txt"
        good_txt.write_text("正常文件。", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            data_dir=str(tmp_path),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        assert stats["errors"] >= 1
        assert stats["processed"] >= 1  # the .txt should still succeed
