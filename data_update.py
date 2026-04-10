"""
data_update.py — CLI function to orchestrate the directory traversal
and ingestion pipeline for the Taiwan carbon market RAG system.

Two-stage pipeline:
  1. extract_to_processed: raw/ → processed/ (multi-format → pure .txt)
  2. run_ingestion_pipeline: processed/ → ChromaDB (chunk → embed → store)

Usage:
    python data_update.py <raw_directory> [--processed-dir ./data/processed] [--db-path ./db/chroma]
"""
import logging
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List


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


def extract_to_processed(
    raw_dir: str,
    processed_dir: str,
) -> Dict[str, int]:
    """
    Stage 1: Extract text from raw multi-format files and write pure .txt
    files into the processed directory.

    Args:
        raw_dir:       Path to the directory containing raw source files.
        processed_dir: Path to the output directory for extracted .txt files.

    Returns:
        Stats dict with keys: extracted, errors.
    """
    stats = {"extracted": 0, "errors": 0}

    # Auto-create output directory
    os.makedirs(processed_dir, exist_ok=True)

    files = discover_files(raw_dir)
    if not files:
        return stats

    for file_path in files:
        try:
            from src.processors import ProcessorFactory
            processor = ProcessorFactory.get_processor(file_path)
            text = processor.extract_text(file_path)

            # Write as .txt with the same stem
            out_name = Path(file_path).stem + ".txt"
            out_path = Path(processed_dir) / out_name
            out_path.write_text(text, encoding="utf-8")

            stats["extracted"] += 1
            logger.info("Extracted: %s → %s", Path(file_path).name, out_name)

        except Exception as exc:
            logger.warning("Failed to extract %s: %s", file_path, exc)
            stats["errors"] += 1

    return stats


def run_ingestion_pipeline(
    processed_dir: str,
    db_path: str = "./db/chroma",
) -> Dict[str, int]:
    """
    Stage 2: Read processed .txt files, chunk them, and store in ChromaDB.

    Args:
        processed_dir: Directory containing pure .txt files ready for chunking.
        db_path:       Path for persistent ChromaDB storage.

    Returns:
        Stats dict with keys: processed, skipped, errors.
    """
    stats = {"processed": 0, "skipped": 0, "errors": 0}

    files = discover_files(processed_dir)
    if not files:
        return stats

    from src.store import VectorStore
    from src.chunker import ChunkStrategy

    store = VectorStore(db_path=db_path)
    chunker = ChunkStrategy()

    for file_path in files:
        try:
            text = Path(file_path).read_text(encoding="utf-8")

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

    parser = argparse.ArgumentParser(description="Taiwan carbon market RAG system data ingestion script.")
    parser.add_argument("raw_directory", nargs="?", default="data/raw", help="Path to the directory containing raw source files (default: data/raw)")
    parser.add_argument("--processed-dir", default="./data/processed", help="Path to the output directory for extracted .txt files")
    parser.add_argument("--db-path", default="./db/chroma", help="Path for persistent ChromaDB storage")
    
    args = parser.parse_args()

    raw_directory = args.raw_directory
    processed = args.processed_dir
    db = args.db_path

    # Stage 1: Extract
    print("=== Stage 1: Extracting raw → processed ===")
    extract_stats = extract_to_processed(raw_dir=raw_directory, processed_dir=processed)
    print(f"  Extracted: {extract_stats['extracted']}, Errors: {extract_stats['errors']}")

    # Stage 2: Ingest
    print("=== Stage 2: Chunking + storing → ChromaDB ===")
    ingest_stats = run_ingestion_pipeline(processed_dir=processed, db_path=db)
    print(f"  Processed: {ingest_stats['processed']}, Errors: {ingest_stats['errors']}")
