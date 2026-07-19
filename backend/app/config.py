import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()
LLM_MODEL = os.getenv("FOUNDERPULSE_LLM_MODEL", "gpt-4o-mini")

DATA_DIR = BACKEND_DIR / "data"
CASES_DIR = DATA_DIR / "cases"
CASES_DIR.mkdir(parents=True, exist_ok=True)


def require_keys() -> None:
    missing = [
        name
        for name, val in [("OPENAI_API_KEY", OPENAI_API_KEY), ("TAVILY_API_KEY", TAVILY_API_KEY)]
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"Missing required keys in backend/.env: {', '.join(missing)}. "
            "Copy backend/.env.example to backend/.env and fill them in."
        )
