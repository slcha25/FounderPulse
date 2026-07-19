"""Case memory (blueprint section 22): one immutable JSON file per case on disk for v1.

A real deployment moves this to Postgres + object storage; the file boundary here mirrors
the "tenant and case authorization" retrieval boundary so it is a drop-in swap later.
"""

import json

from .config import CASES_DIR

CONTACT_FILE = CASES_DIR.parent / "contact_messages.json"


def save_case(case_id: str, data: dict) -> None:
    path = CASES_DIR / f"{case_id}.json"
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def load_case(case_id: str) -> dict | None:
    path = CASES_DIR / f"{case_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_cases() -> list[dict]:
    summaries = []
    for path in sorted(CASES_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        summaries.append(
            {
                "case_id": data.get("case_id"),
                "company_name": data.get("company_name"),
                "created_at": data.get("created_at"),
                "decision_class": (data.get("decision") or {}).get("decision_class"),
                "weighted_score": (data.get("decision") or {}).get("weighted_score"),
                "human_decision": data.get("human_decision"),
                "decision_due_at": data.get("decision_due_at"),
            }
        )
    return summaries


def save_contact_message(data: dict) -> None:
    messages = load_contact_messages()
    messages.append(data)
    CONTACT_FILE.write_text(json.dumps(messages, indent=2, default=str), encoding="utf-8")


def load_contact_messages() -> list[dict]:
    if not CONTACT_FILE.exists():
        return []
    return json.loads(CONTACT_FILE.read_text(encoding="utf-8"))
