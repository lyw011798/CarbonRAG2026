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
import json
import hashlib
from pathlib import Path
from typing import Dict, List


try:
    from src.store import VectorStore
except Exception:
    VectorStore = None


logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".html"}

def get_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_hashes(processed_dir: str) -> Dict[str, str]:
    hash_file = Path(processed_dir) / ".hashes.json"
    if hash_file.exists():
        try:
            return json.loads(hash_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to load hash file: %s", e)
    return {}

def save_hashes(processed_dir: str, hashes: Dict[str, str]) -> None:
    hash_file = Path(processed_dir) / ".hashes.json"
    os.makedirs(processed_dir, exist_ok=True)
    hash_file.write_text(json.dumps(hashes, indent=2), encoding="utf-8")

def clear_processed_artifacts(processed_dir: str) -> None:
    p_dir = Path(processed_dir)
    if not p_dir.exists():
        return
    for item in p_dir.iterdir():
        if item.is_file() and (item.suffix == ".txt" or item.name == ".hashes.json"):
            try:
                item.unlink()
                logger.info("Deleted %s", item.name)
            except Exception as e:
                logger.warning("Failed to delete %s: %s", item.name, e)


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
    run_stages: List[str] = None,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Stage 1: Extract text from raw multi-format files and write pure .txt
    files into the processed directory.

    Args:
        raw_dir:       Path to the directory containing raw source files.
        processed_dir: Path to the output directory for extracted .txt files.
        run_stages:    List of stages allowed to run.
        dry_run:       Dry run boolean check.

    Returns:
        Stats dict with keys: extracted, errors, skipped.
    """
    if run_stages is None:
        run_stages = ["extract", "clean", "chunk", "embed", "store"]
    
    stats = {"extracted": 0, "errors": 0, "skipped": 0}

    if "extract" not in run_stages:
        logger.info("Skipping extract stage due to --stages parameter.")
        return stats

    if not dry_run:
        os.makedirs(processed_dir, exist_ok=True)

    files = discover_files(raw_dir)
    if not files:
        return stats

    hashes = load_hashes(processed_dir)
    updated_hashes = False

    for file_path in files:
        out_name = Path(file_path).stem + ".txt"
        out_path = Path(processed_dir) / out_name

        file_hash = get_file_hash(file_path)

        if file_path in hashes and hashes[file_path] == file_hash and out_path.exists():
            stats["skipped"] += 1
            logger.info("Skipped (unmodified): %s", Path(file_path).name)
            continue

        try:
            from src.processors import ProcessorFactory
            if not dry_run:
                processor = ProcessorFactory.get_processor(file_path)
                text = processor.extract_text(file_path)
                out_path.write_text(text, encoding="utf-8")
                hashes[file_path] = file_hash
                updated_hashes = True
            
            stats["extracted"] += 1
            logger.info("Extracted: %s → %s", Path(file_path).name, out_name)

        except Exception as exc:
            logger.warning("Failed to extract %s: %s", file_path, exc)
            stats["errors"] += 1

    if updated_hashes and not dry_run:
        save_hashes(processed_dir, hashes)

    return stats

def clean_processed_texts(
    processed_dir: str,
    run_stages: List[str] = None,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Stage 1.5: Clean extracted text files in place if 'clean' stage is active.
    """
    if run_stages is None:
        run_stages = ["extract", "clean", "chunk", "embed", "store"]

    stats = {"cleaned": 0, "errors": 0}

    if "clean" not in run_stages:
        logger.info("Skipping clean stage due to --stages parameter.")
        return stats

    files = discover_files(processed_dir)
    if not files:
        return stats

    for file_path in files:
        if dry_run:
            logger.info("Dry-run: clean %s", Path(file_path).name)
            stats["cleaned"] += 1
            continue

        try:
            p = Path(file_path)
            content = p.read_text(encoding="utf-8")
            # Minimal viable placeholder for clearing whitespace bloat
            import re
            clean_content = re.sub(r'\n{3,}', '\n\n', content)
            if content != clean_content:
                p.write_text(clean_content, encoding="utf-8")
                stats["cleaned"] += 1
                logger.info("Cleaned: %s", p.name)
        except Exception as exc:
            logger.warning("Failed to clean %s: %s", file_path, exc)
            stats["errors"] += 1

    return stats


def run_ingestion_pipeline(
    processed_dir: str,
    db_path: str = "./db/chroma",
    run_stages: List[str] = None,
    dry_run: bool = False
) -> Dict[str, int]:
    """
    Stage 2: Read processed .txt files, chunk them, and store in ChromaDB.
    """
    if run_stages is None:
        run_stages = ["extract", "clean", "chunk", "embed", "store"]

    stats = {"processed": 0, "skipped": 0, "errors": 0}

    # If this phase is skipped entirely, exit early
    if not any(stage in run_stages for stage in ["chunk", "embed", "store"]):
        logger.info("Skipping ingestion stages completely due to --stages parameter.")
        return stats

    files = discover_files(processed_dir)
    if not files:
        return stats

    from src.chunker import ChunkStrategy

    store_cls = VectorStore
    if store_cls is None:
        from src.store import VectorStore as store_cls

    store = store_cls(db_path=db_path) if "store" in run_stages or "embed" in run_stages else None
    chunker = ChunkStrategy()

    for file_path in files:
        try:
            # 3.1 Data loader stage
            text = Path(file_path).read_text(encoding="utf-8")

            metadata = {
                "source": file_path,
                "filename": Path(file_path).name,
            }

            chunks = []
            # 3.2 Encapsulate chunking loop
            if "chunk" in run_stages:
                chunks = chunker.split_text(text, initial_metadata=metadata)
            else:
                logger.info("Chunking disabled. Pipeline assumes existing memory chunks for %s.", metadata["filename"])
                continue # In our in-memory pipeline, chunk must process text.

            # 4.2 and 4.3 Isolate embed and store + dry run 
            if chunks and ("embed" in run_stages or "store" in run_stages):
                if not dry_run:
                    store.add_documents(chunks)
                    logger.info("Embedded and stored %d chunks from %s", len(chunks), metadata["filename"])
                else:
                    logger.info("Dry-run: Would embed/store %d chunks from %s", len(chunks), metadata["filename"])

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
    parser.add_argument("--stages", nargs="+", choices=["extract", "clean", "chunk", "embed", "store"], default=["extract", "clean", "chunk", "embed", "store"], help="Specific pipeline stages to execute")
    parser.add_argument("--rebuild", action="store_true", help="Wipe past artifacts and cache before running")
    parser.add_argument("--dry-run", action="store_true", help="Preview expected operations without mutating state")
    
    args = parser.parse_args()

    raw_directory = args.raw_directory
    processed = args.processed_dir
    db = args.db_path

    if args.rebuild and not args.dry_run:
        print("=== Rebuilding: Clearing existing artifacts ===")
        clear_processed_artifacts(processed)

    if args.dry_run:
        print("=== DRY RUN ENABLED: No files or database will be modified ===")

    # Stage 1: Extract
    print("=== Stage 1: Extracting raw → processed ===")
    extract_stats = extract_to_processed(raw_dir=raw_directory, processed_dir=processed, run_stages=args.stages, dry_run=args.dry_run)
    print(f"  Extracted: {extract_stats['extracted']}, Skipped: {extract_stats['skipped']}, Errors: {extract_stats['errors']}")

    # Stage 1.5: Clean
    print("=== Stage 1.5: Cleaning processed documents ===")
    clean_stats = clean_processed_texts(processed_dir=processed, run_stages=args.stages, dry_run=args.dry_run)
    print(f"  Cleaned: {clean_stats['cleaned']}, Errors: {clean_stats['errors']}")

    # Stage 2: Ingest
    print("=== Stage 2: Chunking + storing → ChromaDB ===")
    ingest_stats = run_ingestion_pipeline(processed_dir=processed, db_path=db, run_stages=args.stages, dry_run=args.dry_run)
    print(f"  Processed: {ingest_stats['processed']}, Skipped: {ingest_stats['skipped']}, Errors: {ingest_stats['errors']}")
