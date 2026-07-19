"""Shared runner for all six Scanning Agents (blueprint stage 5 / FR-06 / FR-07).

Each domain agent (founder, market, product, competition, financial, risk) is just this
runner plus a mission string and a subcriteria list — one prompt contract, one JSON schema,
so Decision Agent and the memo renderer can treat every report the same way.
"""

from ...clients import llm_client
from ...clients.llm_client import UsageTracker
from ...prompts.base_prompt import build_system_prompt
from ...schemas import AnalysisReport, StartupProfile

SCANNING_OUTPUT_SCHEMA = (
    '{"score": float (0.0-10.0, one decimal), "confidence": float (0.00-1.00), '
    '"evidence_for": [evidence_id str], "evidence_against": [evidence_id str], '
    '"strengths": [str], '
    '"risks": [{"description": str, "severity": "low"|"medium"|"high", "likelihood": "low"|"medium"|"high"}], '
    '"missing_information": [str], '
    '"recommendation": "pass_to_decision"|"need_more_research"|"material_concern", '
    '"sensitivity": str}'
)

SCORE_ANCHOR_RULE = (
    "Score anchors: 9-10 exceptional and strongly corroborated; 7-8.9 strong with manageable "
    "limitations; 5-6.9 mixed/average with material unknowns; 3-4.9 weak with important "
    "deficiencies; 0-2.9 critical concern or evidence directly contradicts the claim. "
    "A high score built on thin evidence coverage must be paired with lower confidence, not "
    "presented as a strong score alone."
)


def _profile_context(profile: StartupProfile) -> str:
    claims_text = "\n".join(
        f"- {c.get('text')} (evidence: {', '.join(c.get('evidence_ids', []))})" for c in profile.claims
    )
    return (
        f"Company: {profile.company_name}\n"
        f"One-liner: {profile.one_liner or 'unknown'}\n"
        f"Stage: {profile.stage or 'unknown'} | Sector: {profile.sector or 'unknown'}\n"
        f"Founders: {', '.join(profile.founders) or 'unknown'}\n"
        f"Product: {profile.product_summary or 'unknown'}\n"
        f"Market: {profile.market_summary or 'unknown'}\n"
        f"Competition: {profile.competition_summary or 'unknown'}\n"
        f"Traction: {profile.traction_summary or 'unknown'}\n"
        f"Financing: {profile.financing_summary or 'unknown'}\n\n"
        f"CLAIMS WITH CITATIONS:\n{claims_text or 'none recorded'}"
    )


async def run_scanning_agent(
    *,
    agent_key: str,
    agent_label: str,
    mission: str,
    subcriteria: list[str],
    profile: StartupProfile,
    tracker: UsageTracker,
    progress=None,
) -> AnalysisReport:
    if progress is not None:
        progress.emit("scanning", agent_key, "started", detail=f"{agent_label} analyzing…")
    system_prompt = build_system_prompt(
        agent_name=agent_label,
        mission=mission,
        extra_rules=[
            SCORE_ANCHOR_RULE,
            f"Weigh these subcriteria when forming the score: {', '.join(subcriteria)}.",
            "Cite only evidence_id values that appear in the claims below; if none support a "
            "conclusion, say so in missing_information instead of citing an unrelated id.",
        ],
        output_schema_hint=SCANNING_OUTPUT_SCHEMA,
    )
    user_prompt = _profile_context(profile)
    data = await llm_client.call_json(system_prompt, user_prompt, label=agent_key, tracker=tracker, max_tokens=500)
    data["agent"] = agent_key
    report = AnalysisReport(**data)
    if progress is not None:
        progress.emit(
            "scanning", agent_key, "done",
            detail=f"score {report.score}/10, confidence {report.confidence:.2f}",
            score=report.score, confidence=report.confidence, recommendation=report.recommendation.value,
        )
    return report
