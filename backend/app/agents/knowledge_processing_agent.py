"""Knowledge Processing Agent (blueprint stage 4): builds the normalized, cited StartupProfile.

Rules match blueprint FR-05 and the earlier design notes: only organize and cite, never analyze,
never give an opinion, and prefer accuracy over completeness.
"""

from ..clients import llm_client
from ..clients.llm_client import UsageTracker
from ..prompts.base_prompt import build_system_prompt
from ..schemas import EvidenceRecord, StartupProfile

SYSTEM_PROMPT = build_system_prompt(
    agent_name="Knowledge Processing Agent",
    mission=(
        "Convert raw evidence records into one normalized StartupProfile. "
        "You only organize and cite; you never analyze, score or give an opinion."
    ),
    extra_rules=[
        "Only use the evidence provided below. Do not invent facts.",
        "Every entry in claims[] must include evidence_ids pointing at the [eN] ids given below.",
        "If information for a field is not present in the evidence, leave it null or an empty list "
        "instead of guessing.",
        "Prefer accuracy over completeness: a missing field is better than a fabricated one.",
        "Evidence marked AUTHORITATIVE (analyst-uploaded documents, or the company's own site) is the "
        "ground truth for company identity, product and traction. Common company names collide with "
        "unrelated real businesses in web search — if a WEB RESEARCH item describes a different product, "
        "sector or organization than the AUTHORITATIVE evidence (or than the stated sector), do not merge "
        "it into the profile or claims[]; it is very likely a different company with the same name.",
        "If there is no AUTHORITATIVE evidence and WEB RESEARCH items disagree with each other about what "
        "the company even does, leave the affected fields null rather than guessing which source is right.",
    ],
    output_schema_hint=(
        '{"company_name": str, "one_liner": str|null, "founders": [str], '
        '"product_summary": str|null, "market_summary": str|null, '
        '"competition_summary": str|null, "traction_summary": str|null, '
        '"financing_summary": str|null, '
        '"claims": [{"text": str, "evidence_ids": [str]}]}'
    ),
)

MAX_EVIDENCE_CHARS = 7000


def _format_evidence(evidence: list[EvidenceRecord]) -> str:
    authoritative = [e for e in evidence if e.source_type == "first_party"]
    web = [e for e in evidence if e.source_type != "first_party"]

    def _fmt(record: EvidenceRecord) -> str:
        return (
            f"[{record.evidence_id}] ({record.claim_context} | {record.source_type}) "
            f"{record.title} — {record.url}\n{record.excerpt}"
        )

    parts = []
    if authoritative:
        parts.append("=== AUTHORITATIVE (analyst-uploaded / company's own site) ===\n" + "\n\n".join(_fmt(e) for e in authoritative))
    if web:
        parts.append("=== WEB RESEARCH (cross-check against the authoritative section above) ===\n" + "\n\n".join(_fmt(e) for e in web))
    text = "\n\n".join(parts)
    return text[:MAX_EVIDENCE_CHARS]


async def build_profile(
    company_name: str,
    company_url: str | None,
    stage: str | None,
    sector: str | None,
    evidence: list[EvidenceRecord],
    tracker: UsageTracker,
    progress=None,
) -> StartupProfile:
    if progress is not None:
        progress.emit("knowledge_processing", None, "started", detail=f"Normalizing {len(evidence)} evidence records…")
    user_prompt = (
        f"Company: {company_name}\nWebsite: {company_url or 'unknown'}\n"
        f"Stated stage: {stage or 'unknown'}\nStated sector: {sector or 'unknown'}\n\n"
        f"EVIDENCE RECORDS:\n{_format_evidence(evidence)}"
    )
    data = await llm_client.call_json(
        SYSTEM_PROMPT, user_prompt, label="knowledge_processing", tracker=tracker, max_tokens=900
    )
    data["company_name"] = data.get("company_name") or company_name
    data["company_url"] = company_url
    data["stage"] = stage
    data["sector"] = sector
    profile = StartupProfile(**data)
    if progress is not None:
        progress.emit("knowledge_processing", None, "done", detail=profile.one_liner or "Startup profile built")
    return profile
