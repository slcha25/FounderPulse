"""FounderPulse API (blueprint section 24, trimmed to what v1 needs).

Case intake now runs as a background asyncio task so the browser can watch it happen live via
SSE (POST /api/cases/start returns a run_id immediately; GET /api/runs/{run_id}/stream streams
progress events until the case is ready).
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config, document_parser, memory_store, orchestrator
from .progress import RUNS, create_run
from .schemas import ContactMessage, HumanDecision

config.require_keys()

app = FastAPI(title="FounderPulse API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB per file is generous for a pitch deck PDF


class HumanDecisionRequest(BaseModel):
    outcome: str
    rationale: str
    reviewer: str
    reason_code: str | None = None
    override: bool = False


class ContactRequest(BaseModel):
    name: str
    email: str
    message: str


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": config.LLM_MODEL}


@app.post("/api/cases/start")
async def start_case(
    company_name: str = Form(...),
    company_url: str | None = Form(None),
    stage: str | None = Form(None),
    sector: str | None = Form(None),
    thesis_notes: str | None = Form(None),
    files: list[UploadFile] | None = File(default=None),
):
    company_name = company_name.strip()
    if not company_name:
        raise HTTPException(400, "company_name is required")

    uploaded_docs: list[tuple[str, str]] = []
    for f in files or []:
        content = await f.read()
        if not content or len(content) > MAX_UPLOAD_BYTES:
            continue
        text = document_parser.extract_text(f.filename or "document", content)
        if text:
            uploaded_docs.append((f.filename or "document", text))

    tracker = create_run()

    async def _execute() -> None:
        try:
            case = await orchestrator.run_case(
                company_name,
                company_url or None,
                stage or None,
                sector or None,
                thesis_notes or None,
                uploaded_docs or None,
                tracker,
            )
            tracker.result = case
            tracker.emit("complete", None, "done", detail="Case complete", case_id=case["case_id"])
        except Exception as exc:
            tracker.error = str(exc)
            tracker.emit("complete", None, "error", detail=str(exc))
        finally:
            tracker.done = True

    asyncio.create_task(_execute())
    return {"run_id": tracker.run_id}


@app.get("/api/runs/{run_id}/stream")
async def stream_run(run_id: str):
    tracker = RUNS.get(run_id)
    if tracker is None:
        raise HTTPException(404, "run not found")

    async def event_gen():
        idx = 0
        while True:
            if idx < len(tracker.events):
                event = tracker.events[idx]
                idx += 1
                yield f"data: {json.dumps(event)}\n\n"
                if event["stage"] == "complete":
                    break
            elif tracker.done:
                break
            else:
                await asyncio.sleep(0.15)

    return StreamingResponse(event_gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.get("/api/cases")
async def list_cases():
    return memory_store.list_cases()


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    case = memory_store.load_case(case_id)
    if case is None:
        raise HTTPException(404, "case not found")
    return case


@app.post("/api/cases/{case_id}/human-decision")
async def record_human_decision(case_id: str, payload: HumanDecisionRequest):
    case = memory_store.load_case(case_id)
    if case is None:
        raise HTTPException(404, "case not found")
    if payload.outcome not in ("accept", "reject"):
        raise HTTPException(400, "outcome must be 'accept' or 'reject'")

    decided_at = datetime.now(timezone.utc).isoformat()
    deadline_met = decided_at <= case["decision_due_at"]

    human_decision = HumanDecision(
        outcome=payload.outcome,
        reason_code=payload.reason_code,
        rationale=payload.rationale,
        reviewer=payload.reviewer,
        decided_at=decided_at,
        deadline_met=deadline_met,
        override=payload.override,
    )
    case["human_decision"] = human_decision.model_dump(mode="json")
    memory_store.save_case(case_id, case)
    return case


@app.post("/api/contact")
async def submit_contact(payload: ContactRequest):
    name = payload.name.strip()
    email = payload.email.strip()
    message = payload.message.strip()
    if not name or not email or not message:
        raise HTTPException(400, "name, email and message are required")

    record = ContactMessage(
        message_id=f"msg_{uuid.uuid4().hex[:10]}",
        name=name,
        email=email,
        message=message,
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )
    memory_store.save_contact_message(record.model_dump(mode="json"))
    return {"status": "received"}


@app.get("/api/contact")
async def list_contact_messages():
    return memory_store.load_contact_messages()


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
