from deepagents.graph import create_deep_agent
from deepagents.state import DeepAgentState
from deepagents.sub_agent import SubAgent

# Ensure .env is loaded when the package is imported, without failing if dotenv is missing
try:
    from dotenv import load_dotenv  # type: ignore
    from pathlib import Path

    # Try loading a .env from the project root (two levels up from this file: deepagents/__init__.py -> src -> project root)
    _project_root = Path(__file__).resolve().parents[2]
    _dotenv_path = _project_root / ".env"
    if _dotenv_path.exists():
        load_dotenv(dotenv_path=_dotenv_path, override=False)
    else:
        # Fallback to default search in current working directory
        load_dotenv()
except Exception:
    pass