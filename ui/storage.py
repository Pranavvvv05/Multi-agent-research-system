"""
ui/storage.py
-------------
Lightweight file-based persistence so History and Settings survive a
page switch (Streamlit session_state does NOT persist across a full
app restart, and multi-page apps re-run scripts often). Uses the
project's own data/processed/ folder — no new dependency, no DB setup.

If a teammate later adds a real database (the synopsis mentions SQLite
as optional), swap the functions below for DB calls; the rest of the
UI only calls these functions, never touches files directly.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "processed"
HISTORY_FILE = DATA_DIR / "history.jsonl"
KB_MANIFEST_FILE = DATA_DIR / "kb_manifest.json"
CONFIG_FILE = DATA_DIR / "app_config.json"


# ── Run history ──────────────────────────────────────────────────────────
def log_run(record: dict):
    """record should include: topic, timestamp, relevance, quality,
    latency, source_count, report_markdown (see app.py call site)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    records = []
    with open(HISTORY_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return list(reversed(records))  # newest first


# ── Knowledge base manifest (what's been ingested into ChromaDB) ────────
def load_kb_manifest() -> list[dict]:
    if not KB_MANIFEST_FILE.exists():
        return []
    return json.loads(KB_MANIFEST_FILE.read_text(encoding="utf-8"))


def save_kb_manifest(entries: list[dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KB_MANIFEST_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Non-secret config (chunk size, top-k, etc.) ──────────────────────────
DEFAULT_CONFIG = {
    "model": "gemini-2.0-flash",
    "chunk_size": 800,
    "chunk_overlap": 100,
    "top_k": 5,
    "temperature": 0.3,
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {**DEFAULT_CONFIG, **saved}


def save_config(config: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")