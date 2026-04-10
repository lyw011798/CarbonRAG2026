import argparse
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

from src.store import VectorStore
from src.query import RAGQuery
from src.builder import SkillBuilder

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Taiwan Carbon Market RAG Skill Builder CLI")
    parser.add_argument("--db-path", type=str, default="./db/chroma", help="Path to ChromaDB directory")
    parser.add_argument("--model", type=str, default="gemini/gemini-2.5-flash", help="LiteLLM model string to use")
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve per skill query")
    parser.add_argument("--mock", action="store_true", help="Use mock mode to bypass actual LLM API calls")
    parser.add_argument("--output", type=str, default="skill.md", help="Output Markdown file path")
    
    args = parser.parse_args()
    
    logger.info(f"Initializing VectorStore from {args.db_path}...")
    try:
        vector_store = VectorStore(db_path=args.db_path)
    except Exception as e:
        logger.error(f"Failed to initialize VectorStore: {e}")
        sys.exit(1)
        
    query_engine = RAGQuery(vector_store=vector_store, model=args.model)
    builder = SkillBuilder(query_engine=query_engine)
    
    mode_text = "MOCK mode" if args.mock else f"LIVE mode ({args.model})"
    logger.info(f"Generating skill reference text in {mode_text}. This may take a moment...")
    
    try:
        content = builder.build_skill_content(
            n_results=args.top_k, 
            use_mock=args.mock
        )
        
        output_path = Path(args.output)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Successfully generated and wrote skill reference to: {output_path.absolute()}")
        
    except Exception as e:
        logger.error(f"Failed to generate skill content: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
