import argparse
import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def format_citations(sources: list) -> str:
    """Formats the list of sources into a readable citation string."""
    if not sources:
        return ""
    
    citation_lines = [f"{Colors.YELLOW}{Colors.BOLD}Citations:{Colors.RESET}"]
    for i, source in enumerate(sources, 1):
        filename = source.get("filename", "Unknown File")
        article = source.get("article", "Unknown Article")
        citation_lines.append(f"{Colors.YELLOW}  [{i}] {filename} -> {article}{Colors.RESET}")
    
    return "\n".join(citation_lines)

def interactive_loop(query_engine, n_results: int):
    """Runs the interactive QA loop."""
    print(f"\n{Colors.HEADER}=== Taiwan Carbon Market RAG System ==={Colors.RESET}")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            # Get user input
            question = input(f"{Colors.GREEN}{Colors.BOLD}You: {Colors.RESET}").strip()
            
            if not question:
                continue
                
            if question.lower() in ['exit', 'quit']:
                print(f"{Colors.CYAN}Exiting RAG system. Goodbye!{Colors.RESET}")
                break
                
            print(f"{Colors.CYAN}Thinking...{Colors.RESET}")
            
            # Perform query
            result = query_engine.query(
                question=question, 
                n_results=n_results
            )
            
            answer = result["answer"]
            sources = result["sources"]
            
            # Print answer
            print(f"\n{Colors.BLUE}{Colors.BOLD}Assistant: {Colors.RESET}{answer}")
            
            # Print citations
            citations_str = format_citations(sources)
            if citations_str:
                print(f"\n{citations_str}")
            print("\n" + "-"*50 + "\n")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}Exiting RAG system. Goodbye!{Colors.RESET}")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Taiwan Carbon Market RAG Interactive CLI")
    parser.add_argument("--db-path", type=str, default="./db/chroma", help="Path to ChromaDB directory")
    parser.add_argument("--model", type=str, default="gemini/gemini-2.5-flash", help="LiteLLM model string to use")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve per query")
    
    args = parser.parse_args()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.store import VectorStore
    from src.query import RAGQuery
    
    print(f"{Colors.CYAN}Initializing VectorStore at {args.db_path}...{Colors.RESET}")
    try:
        vector_store = VectorStore(db_path=args.db_path)
    except Exception as e:
        logger.error(f"Failed to initialize VectorStore: {e}")
        sys.exit(1)
        
    query_engine = RAGQuery(vector_store=vector_store, model=args.model)
    
    interactive_loop(
        query_engine=query_engine,
        n_results=args.top_k
    )

if __name__ == "__main__":
    main()
