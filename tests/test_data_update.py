"""
TDD tests for data_update.py — the CLI ingestion pipeline orchestrator.

Tests follow Arrange-Act-Assert.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from data_update import (
    discover_files,
    extract_to_processed,
    run_ingestion_pipeline,
)


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
# extract_to_processed
# ---------------------------------------------------------------------------

class TestExtractToProcessed:
    """Tests for the raw → processed extraction stage."""

    def test_extract_creates_txt_from_raw_txt(self, tmp_path):
        """A .txt file in raw/ should produce a .txt in processed/."""
        # Arrange
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (raw_dir / "law.txt").write_text("第一條 碳費管理。", encoding="utf-8")

        # Act
        stats = extract_to_processed(str(raw_dir), str(processed_dir))

        # Assert
        output_file = processed_dir / "law.txt"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "第一條" in content
        assert stats["extracted"] == 1

    def test_extract_creates_txt_from_raw_md(self, tmp_path):
        """A .md file in raw/ should produce a .txt in processed/."""
        # Arrange
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (raw_dir / "rules.md").write_text("# 碳費收費辦法\n\n第一條 依據氣候法。", encoding="utf-8")

        # Act
        stats = extract_to_processed(str(raw_dir), str(processed_dir))

        # Assert
        output_file = processed_dir / "rules.txt"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "碳費收費辦法" in content
        assert stats["extracted"] == 1

    def test_extract_creates_txt_from_raw_html(self, tmp_path):
        """A .html file in raw/ should produce a .txt in processed/."""
        # Arrange
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (raw_dir / "page.html").write_text(
            "<html><body><p>碳交易資訊</p></body></html>", encoding="utf-8"
        )

        # Act
        stats = extract_to_processed(str(raw_dir), str(processed_dir))

        # Assert
        output_file = processed_dir / "page.txt"
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "碳交易資訊" in content
        assert stats["extracted"] == 1

    def test_extract_creates_processed_dir_if_missing(self, tmp_path):
        """extract_to_processed should auto-create the output directory."""
        # Arrange
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"  # NOT created
        (raw_dir / "doc.txt").write_text("content", encoding="utf-8")

        # Act
        extract_to_processed(str(raw_dir), str(processed_dir))

        # Assert
        assert processed_dir.exists()
        assert (processed_dir / "doc.txt").exists()

    def test_extract_records_errors_for_bad_files(self, tmp_path):
        """Broken files should be counted as errors, not crash the pipeline."""
        # Arrange
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (raw_dir / "broken.pdf").write_bytes(b"not a real pdf")
        (raw_dir / "ok.txt").write_text("good content", encoding="utf-8")

        # Act
        stats = extract_to_processed(str(raw_dir), str(processed_dir))

        # Assert
        assert stats["errors"] >= 1
        assert stats["extracted"] >= 1  # ok.txt should still succeed

    def test_extract_returns_stats(self, tmp_path):
        """extract_to_processed should return a dict with extracted and errors."""
        # Arrange
        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (raw_dir / "a.txt").write_text("aaa", encoding="utf-8")
        (raw_dir / "b.txt").write_text("bbb", encoding="utf-8")

        # Act
        stats = extract_to_processed(str(raw_dir), str(processed_dir))

        # Assert
        assert stats["extracted"] == 2
        assert stats["errors"] == 0


# ---------------------------------------------------------------------------
# run_ingestion_pipeline  (integration-style with mocks for heavy I/O)
# ---------------------------------------------------------------------------

class TestRunIngestionPipeline:
    """Tests for the full ingestion orchestration function (chunk + store)."""

    @patch("data_update.VectorStore")
    def test_pipeline_processes_txt_file(self, MockVectorStore, tmp_path):
        """Pipeline should chunk and store text from processed .txt files."""
        # Arrange
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (processed_dir / "law.txt").write_text(
            "第一條 本法為碳交易管理之基本法。\n第二條 主管機關為環境部。\n第三條 碳費收取方式。",
            encoding="utf-8",
        )
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            processed_dir=str(processed_dir),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        mock_store.add_documents.assert_called_once()
        chunks_arg = mock_store.add_documents.call_args[0][0]
        assert len(chunks_arg) >= 2  # at least 2 articles
        assert stats["processed"] == 1
        assert stats["skipped"] == 0

    @patch("data_update.VectorStore")
    def test_pipeline_skips_unsupported_files(self, MockVectorStore, tmp_path):
        """Pipeline should count unsupported files as skipped, not crash."""
        # Arrange
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (processed_dir / "photo.jpg").write_bytes(b"\xff\xd8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            processed_dir=str(processed_dir),
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
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (processed_dir / "carbon_act.txt").write_text("碳費徵收機制概述。", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        run_ingestion_pipeline(
            processed_dir=str(processed_dir),
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
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        txt_file = processed_dir / "info.txt"
        txt_file.write_text("一般資訊。", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        run_ingestion_pipeline(
            processed_dir=str(processed_dir),
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
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        (processed_dir / "a.txt").write_text("text a", encoding="utf-8")
        (processed_dir / "b.txt").write_text("text b", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            processed_dir=str(processed_dir),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        assert stats["processed"] == 2
        assert "errors" in stats

    @patch("data_update.VectorStore")
    def test_pipeline_handles_errors_gracefully(self, MockVectorStore, tmp_path):
        """If a file read fails, pipeline should record the error and continue."""
        # Arrange
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        # Create a valid file and a directory with .txt extension (will fail to read)
        (processed_dir / "ok.txt").write_text("正常文件。", encoding="utf-8")
        mock_store = MagicMock()
        MockVectorStore.return_value = mock_store

        # Act
        stats = run_ingestion_pipeline(
            processed_dir=str(processed_dir),
            db_path=str(tmp_path / "db"),
        )

        # Assert
        assert stats["processed"] >= 1
