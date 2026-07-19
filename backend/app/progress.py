"""In-memory run progress tracking so the UI can show agents working in real time.

One process, single demo user in mind for v1 — RunTracker instances live in the RUNS dict for
the lifetime of the process. The SSE endpoint in main.py polls tracker.events by index rather
than using a queue, which sidesteps replay/double-delivery issues if a client reconnects.
"""

import time
import uuid

STAGE_LABELS = {
    "sources": "Source Agents",
    "knowledge_processing": "Knowledge Processing Agent",
    "scanning": "Scanning Agent",
    "delegate": "Delegate Agent",
    "decision": "Decision Agent",
    "memo": "Memo Agent",
    "complete": "Complete",
}


class RunTracker:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.events: list[dict] = []
        self.done = False
        self.result: dict | None = None
        self.error: str | None = None

    def emit(self, stage: str, agent: str | None, status: str, detail: str | None = None, **extra) -> None:
        event = {
            "run_id": self.run_id,
            "stage": stage,
            "stage_label": STAGE_LABELS.get(stage, stage),
            "agent": agent,
            "status": status,
            "detail": detail,
            "ts": time.time(),
        }
        event.update(extra)
        self.events.append(event)


RUNS: dict[str, RunTracker] = {}


def create_run() -> RunTracker:
    run_id = f"run_{uuid.uuid4().hex[:10]}"
    tracker = RunTracker(run_id)
    RUNS[run_id] = tracker
    return tracker
