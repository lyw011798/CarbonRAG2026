"""Verify document processors in the current runtime environment."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.processors import ProcessorFactory


SupportedFixture = tuple[str, Callable[[Path], Path]]


def create_text_fixture(directory: Path) -> Path:
    filePath = directory / "sample.txt"
    filePath.write_text("台灣碳費測試文件", encoding="utf-8")
    return filePath


def create_markdown_fixture(directory: Path) -> Path:
    filePath = directory / "sample.md"
    filePath.write_text("# 標題\n\n**自主減量計畫** 測試內容", encoding="utf-8")
    return filePath


def create_html_fixture(directory: Path) -> Path:
    filePath = directory / "sample.html"
    filePath.write_text(
        "<html><body><main><h1>CBAM</h1><p>碳邊境調整機制測試內容</p></main></body></html>",
        encoding="utf-8",
    )
    return filePath


def create_pdf_fixture(directory: Path) -> Path:
    try:
        import fitz
    except ImportError as error:
        raise RuntimeError("PyMuPDF is required to generate the PDF verification fixture.") from error

    filePath = directory / "sample.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Taiwan carbon fee PDF verification")
    document.save(filePath)
    document.close()
    return filePath


def find_existing_file(rawDir: Path, extension: str) -> Path | None:
    if not rawDir.exists():
        return None

    for filePath in rawDir.rglob(f"*{extension}"):
        if filePath.is_file():
            return filePath

    return None


def verify_processor(filePath: Path) -> None:
    processor = ProcessorFactory.get_processor(filePath)
    extractedText = processor.extract_text(filePath)

    if not extractedText.strip():
        raise RuntimeError(f"{filePath.suffix} processor returned empty text for {filePath}.")

    print(f"ok {filePath.suffix}: {filePath}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify registered document processors.")
    parser.add_argument("--raw-dir", default="data/raw", help="Mounted raw data directory to inspect first.")
    args = parser.parse_args()

    rawDir = Path(args.raw_dir)
    fixtures: list[SupportedFixture] = [
        (".pdf", create_pdf_fixture),
        (".txt", create_text_fixture),
        (".md", create_markdown_fixture),
        (".html", create_html_fixture),
    ]

    with tempfile.TemporaryDirectory() as tempDirName:
        tempDir = Path(tempDirName)
        for extension, createFixture in fixtures:
            filePath = find_existing_file(rawDir, extension) or createFixture(tempDir)
            verify_processor(filePath)

    print("All registered document processors verified.")


if __name__ == "__main__":
    main()
