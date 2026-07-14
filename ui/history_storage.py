"""
ui/history_storage.py
----------------------
Simple JSON-file-backed persistent storage for past research runs.
"""

import json
import time
import uuid
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "data" / "history.json"


def _ensure_file():
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def load_history() -> list:
    """Returns all saved runs, most recent first."""
    _ensure_file()
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return sorted(data, key=lambda e: e.get("timestamp", 0), reverse=True)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_history_entry(document_name: str, results: dict, elapsed: float = None, use_rag: bool = None) -> str:
    """Saves one completed pipeline run (scores, sources, report — everything)."""
    _ensure_file()
    history = load_history()

    entry_id = str(uuid.uuid4())
    entry = {
        "id": entry_id,
        "document_name": document_name,
        "timestamp": time.time(),
        "elapsed": elapsed,
        "use_rag": use_rag,
        "results": results,
    }
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return entry_id


def get_history_entry(entry_id: str) -> dict | None:
    for entry in load_history():
        if entry["id"] == entry_id:
            return entry
    return None


def delete_history_entry(entry_id: str) -> None:
    history = [e for e in load_history() if e["id"] != entry_id]
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")