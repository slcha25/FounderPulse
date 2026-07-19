"""Master Orchestrator (blueprint section 25): runs the full due-diligence workflow for one case.

Sources -> Knowledge Processing -> six parallel Scanning Agents -> Delegate -> Decision -> Memo,
then persists the case to memory. Reflection is intentionally not called here — it only makes
sense once a verified outcome exists later, see agents/reflection_agent.py.

Every stage reports to an optional RunTracker (app/progress.py) so the UI can show agents
working in real time via SSE.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from . import memory_store
from .agents import decision_agent, delegate_agent, knowledge_processing_agent, memo_agent, sources_agent
from .agents.scanning import (
    competition_agent,
    financial_agent,
    founder_agent,
    market_agent,
    product_agent,
    risk_agent,
)
from .clients.llm_client import UsageTracker
from .progress import RunTracker
from .schemas import CaseRecord

SCANNING_AGENTS = [founder_agent, market_agent, product_agent, competition_agent, financial_agent, risk_agent]

SLA_HOURS = 24


async def run_case(
    company_name: str,
    company_url: str | None,
    stage: str | None,
    sector: str | None,
    thesis_notes: str | None,
    uploaded_docs: list[tuple[str, str]] | None = None,
    progress: RunTracker | None = None,
) -> dict:
    case_id = f"case_{uuid.uuid4().hex[:10]}"
    tracker = UsageTracker()

    now = datetime.now(timezone.utc)
    application_validated_at = now.isoformat()
    decision_due_at = (now + timedelta(hours=SLA_HOURS)).isoformat()

    evidence = await sources_agent.gather_evidence(company_name, company_url, progress=progress)
    if uploaded_docs:
        upload_evidence = sources_agent.evidence_from_uploads(uploaded_docs, start_counter=len(evidence) + 1)
        evidence = evidence + upload_evidence

    profile = await knowledge_processing_agent.build_profile(
        company_name, company_url, stage, sector, evidence, tracker, progress=progress
    )

    reports_list = await asyncio.gather(
        *(agent.run(profile, tracker, progress=progress) for agent in SCANNING_AGENTS)
    )
    reports = {r.agent: r for r in reports_list}

    delegate_result = delegate_agent.run_delegate(reports, progress=progress)
    decision = await decision_agent.run_decision(reports, delegate_result, tracker, thesis_notes, progress=progress)
    memo_markdown = memo_agent.render_memo(
        profile, reports, delegate_result, decision, evidence, decision_due_at, progress=progress
    )

    case = CaseRecord(
        case_id=case_id,
        company_name=company_name,
        company_url=company_url,
        stage=stage,
        sector=sector,
        thesis_notes=thesis_notes,
        created_at=application_validated_at,
        application_validated_at=application_validated_at,
        decision_due_at=decision_due_at,
        profile=profile,
        evidence=evidence,
        reports=reports,
        delegate=delegate_result,
        decision=decision,
        memo_markdown=memo_markdown,
        human_decision=None,
        cost_summary=tracker.summary(),
    )

    data = case.model_dump(mode="json")
    memory_store.save_case(case_id, data)
    return data
