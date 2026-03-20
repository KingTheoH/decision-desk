import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR}/data/decision_desk.db"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Ensure data dir exists
(BASE_DIR / "data").mkdir(exist_ok=True)
