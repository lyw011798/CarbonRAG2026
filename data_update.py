"""
data_update.py — CLI function to orchestrate the directory traversal
and ingestion pipeline for the Taiwan carbon market RAG system.

Usage:
    python data_update.py <data_directory> [--db-path ./db/chroma]
"""
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List

from src.processors import ProcessorFactory
from src.chunker import ChunkStrategy
from src.store import VectorStore

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".html"}


def discover_files(directory: str) -> List[str]:
    """
    Recursively discover all supported document files in a directory.

    Args:
        directory: Path to the root directory to scan.

    Returns:
        Sorted list of absolute file paths with supported extensions.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = []
    for root, _, filenames in os.walk(dir_path):
        for fname in filenames:
            if Path(fname).suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(str(Path(root) / fname))

    return sorted(files)


def run_ingestion_pipeline(
    data_dir: str,
    db_path: str = "./db/chroma",
) -> Dict[str, int]:
    """
    Orchestrate the full ingestion pipeline:
      1. Discover files
      2. For each file: extract text → chunk → collect
      3. Batch-store all chunks into VectorStore

    Args:
        data_dir:  Root directory containing documents.
        db_path:   Path for persistent ChromaDB storage.

    Returns:
        Stats dict with keys: processed, skipped, errors.
    """
    stats = {"processed": 0, "skipped": 0, "errors": 0}

    files = discover_files(data_dir)
    if not files:
        return stats

    store = VectorStore(db_path=db_path)
    chunker = ChunkStrategy()

    for file_path in files:
        try:
            processor = ProcessorFactory.get_processor(file_path)
            text = processor.extract_text(file_path)

            metadata = {
                "source": file_path,
                "filename": Path(file_path).name,
            }

            chunks = chunker.split_text(text, initial_metadata=metadata)

            if chunks:
                store.add_documents(chunks)

            stats["processed"] += 1

        except Exception as exc:
            logger.warning("Failed to process %s: %s", file_path, exc)
            stats["errors"] += 1

    return stats


# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <data_directory> [--db-path PATH]")
        sys.exit(1)

    data_directory = sys.argv[1]
    db = "./db/chroma"
    if "--db-path" in sys.argv:
        idx = sys.argv.index("--db-path")
        db = sys.argv[idx + 1]

    result = run_ingestion_pipeline(data_dir=data_directory, db_path=db)
    print(f"Done — processed: {result['processed']}, "
          f"skipped: {result['skipped']}, errors: {result['errors']}")
