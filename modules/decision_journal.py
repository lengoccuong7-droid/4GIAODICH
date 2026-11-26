"""Append-only JSONL decision journal with explicit opt-in persistence."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

def append_decision(record: dict, path="data/decision_journal.jsonl") -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(record)
    payload.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
    with target.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    return str(target)

def read_decisions(path="data/decision_journal.jsonl", limit=100) -> list[dict]:
    target = Path(path)
    if not target.exists():
        return []
    with target.open(encoding="utf-8") as f:
        lines = f.readlines()[-max(1, int(limit)):]
    rows = []
    for line in lines:
        try: rows.append(json.loads(line))
        except json.JSONDecodeError: continue
    return rows
