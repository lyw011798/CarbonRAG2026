"""HTTP backend for the Carbon RAG chat demo."""

from __future__ import annotations

import json
import os
import sys
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_DB_PATH = "db/chroma"
DEFAULT_MODEL = "gemini/gemini-2.5-flash"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_dotenv_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs without requiring python-dotenv at startup."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        normalizedKey = key.strip()
        normalizedValue = value.strip().strip('"').strip("'")

        if normalizedKey and normalizedKey not in os.environ:
            os.environ[normalizedKey] = normalizedValue


class BackendState:
    """Lazily owns the RAG query engine so health checks stay lightweight."""

    def __init__(self) -> None:
        self.queryEngine: Any | None = None
        self.dbPath: Path | None = None
        self.skillBuilder: Any | None = None

    @staticmethod
    def get_db_path() -> Path:
        rawDbPath = os.getenv("CHROMA_PERSIST_DIR", DEFAULT_DB_PATH)
        dbPath = Path(rawDbPath)

        if not dbPath.is_absolute():
            dbPath = PROJECT_ROOT / dbPath

        return dbPath

    @staticmethod
    def get_model_name() -> str:
        return os.getenv("RAG_MODEL", DEFAULT_MODEL)

    @staticmethod
    def get_top_k() -> int:
        rawTopK = os.getenv("RAG_TOP_K", "5")

        try:
            topK = int(rawTopK)
        except ValueError as error:
            raise RuntimeError("RAG_TOP_K must be an integer.") from error

        if topK < 1:
            raise RuntimeError("RAG_TOP_K must be greater than zero.")

        return topK

    @staticmethod
    def validate_llm_configuration() -> None:
        modelName = BackendState.get_model_name()
        hasLiteLlmGateway = bool(os.getenv("LITELLM_BASE_URL"))
        hasLiteLlmKey = bool(os.getenv("LITELLM_API_KEY"))
        usesGemini = modelName.startswith("gemini/")

        if hasLiteLlmGateway and not hasLiteLlmKey:
            raise RuntimeError(
                "LITELLM_API_KEY is required when LITELLM_BASE_URL is configured."
            )

        if usesGemini and not os.getenv("GEMINI_API_KEY") and not hasLiteLlmKey:
            raise RuntimeError(
                "GEMINI_API_KEY or LITELLM_API_KEY is required for Gemini chat models."
            )

    @staticmethod
    def is_db_ready(dbPath: Path) -> bool:
        if not dbPath.exists() or not dbPath.is_dir():
            return False

        return any(dbPath.iterdir())

    def get_query_engine(self) -> Any:
        if self.queryEngine is not None:
            return self.queryEngine

        dbPath = self.get_db_path()
        if not self.is_db_ready(dbPath):
            raise RuntimeError(
                "Vector database was not found or is empty. Run "
                "`python data_update.py --rebuild --db-path "
                f"{dbPath}` before using chat."
            )

        self.validate_llm_configuration()

        try:
            from src.query import RAGQuery
            from src.store import VectorStore
        except ImportError as error:
            raise RuntimeError(
                "Backend dependencies are missing. Install Python dependencies with "
                "`pip install -r requirements.txt` in a supported Python environment."
            ) from error

        try:
            vectorStore = VectorStore(db_path=str(dbPath))
            self.queryEngine = RAGQuery(
                vector_store=vectorStore, model=self.get_model_name()
            )
            self.dbPath = dbPath
        except Exception as error:
            raise RuntimeError(
                f"Failed to initialize the RAG engine: {error}"
            ) from error

        return self.queryEngine

    def get_skill_builder(self) -> Any:
        if self.skillBuilder is not None:
            return self.skillBuilder

        query_engine = self.get_query_engine()
        try:
            from src.builder import SkillBuilder

            self.skillBuilder = SkillBuilder(query_engine=query_engine)
        except Exception as error:
            raise RuntimeError(
                f"Failed to initialize the Skill Builder: {error}"
            ) from error

        return self.skillBuilder


state = BackendState()


def make_json_response(
    handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: dict[str, Any]
) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def make_file_download_response(
    handler: BaseHTTPRequestHandler, status: HTTPStatus, content: str, filename: str
) -> None:
    """Return a plain text or markdown file as a download stream."""
    body = content.encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "text/markdown; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Content-Disposition", f'attachment; filename="{filename}"')
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def parse_chat_request(payload: Any) -> str:
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")

    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("Request body must include a non-empty `messages` array.")

    latestUserMessage = None
    for message in reversed(messages):
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        content = message.get("content")
        if role == "user" and isinstance(content, str) and content.strip():
            latestUserMessage = content.strip()
            break

    if latestUserMessage is None:
        raise ValueError(
            "Request messages must include at least one non-empty user message."
        )

    return latestUserMessage


class ChatRequestHandler(BaseHTTPRequestHandler):
    """Serve the local chat API expected by the Vite frontend."""

    server_version = "CarbonRAGBackend/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("%s - - %s\n" % (self.address_string(), format % args))

    def do_OPTIONS(self) -> None:
        make_json_response(self, HTTPStatus.NO_CONTENT, {})

    def do_GET(self) -> None:
        if self.path != "/health":
            make_json_response(
                self, HTTPStatus.NOT_FOUND, {"error": "Route not found."}
            )
            return

        dbPath = state.get_db_path()
        llmReady = True
        llmError = None

        try:
            state.validate_llm_configuration()
        except RuntimeError as error:
            llmReady = False
            llmError = str(error)

        make_json_response(
            self,
            HTTPStatus.OK,
            {
                "status": "ok",
                "dbPath": str(dbPath),
                "dbReady": state.is_db_ready(dbPath),
                "llmReady": llmReady,
                "llmError": llmError,
            },
        )

    def do_POST(self) -> None:
        allowed_paths = {"/chat", "/skill"}
        if self.path not in allowed_paths:
            make_json_response(
                self, HTTPStatus.NOT_FOUND, {"error": f"Route {self.path} not found."}
            )
            return

        try:
            contentLength = int(self.headers.get("Content-Length", "0"))
            rawBody = self.rfile.read(contentLength)
            payload = json.loads(rawBody.decode("utf-8"))
        except json.JSONDecodeError:
            make_json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {"error": "Request body must be valid JSON."},
            )
            return
        except ValueError as error:
            make_json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
            return

        # /chat
        if self.path == "/chat":
            try:
                question = parse_chat_request(payload)
            except ValueError as error:
                make_json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(error)})
                return

            try:
                queryEngine = state.get_query_engine()
                result = queryEngine.query(
                    question=question, n_results=state.get_top_k()
                )
                answer = str(result.get("answer", "")).strip()

                if not answer:
                    make_json_response(
                        self,
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"error": "The chat query returned an empty answer."},
                    )
                    return

                make_json_response(
                    self,
                    HTTPStatus.OK,
                    {"message": {"role": "assistant", "content": answer}},
                )
            except Exception as error:
                make_json_response(
                    self,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": f"Request failed: {error}"},
                )

        # /skill
        elif self.path == "/skill":
            messages = payload.get("messages", [])
            if not isinstance(messages, list) or not messages:
                make_json_response(
                    self,
                    HTTPStatus.BAD_REQUEST,
                    {
                        "error": "Request body must include a non-empty `messages` array."
                    },
                )
                return

            start_time = time.time()
            try:
                sys.stderr.write(f"[/skill] Starting conversation summary generation...\n")
                
                formatted_dialogue = "以下是使用者的歷史對話紀錄：\n\n"
                for msg in messages:
                    if not isinstance(msg, dict):
                        continue
                    role = "使用者" if msg.get("role") == "user" else "AI 助理"
                    content = msg.get("content", "")
                    formatted_dialogue += f"【{role}】: {content}\n\n"

                skillBuilder = state.get_skill_builder()

                markdown_content = skillBuilder.build_conversation_summary(
                    context=formatted_dialogue,
                    n_results=state.get_top_k(),
                    use_mock=False,
                )
                
                elapsed = time.time() - start_time
                sys.stderr.write(f"[/skill] Summary generated in {elapsed:.2f}s\n")

                if not markdown_content:
                    make_json_response(
                        self,
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"error": "Failed to generate skill content."},
                    )
                    return

                make_json_response(
                    self,
                    HTTPStatus.OK,
                    {
                        "filename": "summary.md",
                        "contentType": "text/markdown; charset=utf-8",
                        "content": markdown_content,
                    },
                )
            except Exception as error:
                elapsed = time.time() - start_time
                sys.stderr.write(f"[/skill] Error after {elapsed:.2f}s: {error}\n")
                make_json_response(
                    self,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": f"Request failed: {error}"},
                )


def main() -> None:
    load_dotenv_file(PROJECT_ROOT / ".env")

    host = os.getenv("BACKEND_HOST", DEFAULT_HOST)
    port = int(os.getenv("BACKEND_PORT", str(DEFAULT_PORT)))
    server = ThreadingHTTPServer((host, port), ChatRequestHandler)

    print(f"Carbon RAG backend running at http://{host}:{port}")
    print("Health check: GET /health")
    print("Chat endpoint: POST /chat")
    print("Skill endpoint: POST /skill")
    server.serve_forever()


if __name__ == "__main__":
    main()
