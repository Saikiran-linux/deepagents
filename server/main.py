import os
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Ensure project src is importable when running server directly
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
EXAMPLES_DIR = ROOT_DIR / "examples"
EXAMPLES_RESEARCH_DIR = EXAMPLES_DIR / "research"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(EXAMPLES_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLES_RESEARCH_DIR))


try:
    # Load environment from project root .env if present
    from dotenv import load_dotenv  # type: ignore

    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        load_dotenv(override=False)
except Exception:
    pass


app = FastAPI(title="DeepAgents Server", version="0.1.0")

# Allow local dev by default
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    agent_id: str
    prompt: str
    # Optional: future fields
    recursion_limit: int | None = 1000


def _import_research_agent():
    """Import and return the prebuilt research agent from examples.

    Returns a tuple: (agent, module)
    """
    try:
        # Import from examples/research directory directly
        import research_agent as research_mod  # type: ignore
        research_agent = getattr(research_mod, "agent")
        return research_agent, research_mod
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            f"Failed to import research agent. Ensure package is installed (`pip install -e .`) and examples path is available. Error: {exc}"
        ) from exc


@app.get("/api/agents")
def list_agents() -> Dict[str, Any]:
    """List available agents for selection in the UI."""
    # For now only research is available; this can be extended later
    return {
        "agents": [
            {"id": "research", "name": "Research Agent", "description": "Deep research with web search and report writing"}
        ]
    }


@app.post("/api/agent/run")
async def run_agent(req: RunRequest) -> Dict[str, Any]:
    if req.agent_id != "research":
        raise HTTPException(status_code=400, detail=f"Unknown agent_id: {req.agent_id}")

    # Validate env (Tavily API is required by the example agent tools)
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "TAVILY_API_KEY is not set. Add it to a .env at project root or set environment variable."
            ),
        )

    research_agent, _ = _import_research_agent()

    # Run the agent and capture virtual file outputs
    try:
        result = await research_agent.ainvoke(
            {"messages": [{"role": "user", "content": req.prompt}]},
            {"recursion_limit": req.recursion_limit or 1000},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    files = result.get("files", {}) if isinstance(result, dict) else {}
    report_content = files.get("final_report.md")

    # Also return the last assistant message if present
    messages = result.get("messages", []) if isinstance(result, dict) else []
    last_assistant = None
    if messages:
        for msg in reversed(messages):
            if getattr(msg, "role", None) == "assistant" or (
                isinstance(msg, dict) and msg.get("role") == "assistant"
            ):
                last_assistant = getattr(msg, "content", None) or msg.get("content")
                break

    return {
        "agent_id": req.agent_id,
        "report": report_content,
        "assistant_message": last_assistant,
        "files": {k: (v if isinstance(v, str) else str(v)) for k, v in files.items()},
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_enabled = os.getenv("RELOAD", "1") == "1"

    # Use import string when reload is enabled to avoid uvicorn warning and enable auto-reload
    if reload_enabled:
        uvicorn.run(
            "server.main:app",
            host=host,
            port=port,
            reload=True,
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
        )


