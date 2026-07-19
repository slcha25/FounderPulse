"""Decision Agent (blueprint stage 7): synthesizes reports into a recommendation.

The numeric classification and weighted score are computed deterministically in Python
(section 14's decision policy) so they are reproducible and auditable. The single LLM call
only writes the narrative — it is explicitly told not to change the classification and to
only reuse strengths/risks that already appear in the six reports, so it cannot silently
resolve a disagreement by picking the more favorable side (section 15).
"""

from ..clients import llm_client
from ..clients.llm_client import UsageTracker
from ..prompts.base_prompt import build_system_prompt
from ..schemas import AnalysisReport, DecisionClass, DecisionRecommendation, DelegateResult
from ..scoring import (
    DIMENSION_WEIGHTS,
    MORE_RESEARCH_SCORE_FLOOR,
    RECOMMEND_CONFIDENCE_THRESHOLD,
    RECOMMEND_SCORE_THRESHOLD,
)

SYSTEM_PROMPT = build_system_prompt(
    agent_name="Decision Agent",
    mission=(
        "Write the narrative portion of an investment recommendation from six specialist "
        "reports. The numeric classification and weighted score are already computed "
        "deterministically and given to you — do not change them or state a different score."
    ),
    extra_rules=[
        "Only use strengths, risks and missing_information that already appear in the reports given to you.",
        "If two reports disagree or point in different directions, say so explicitly instead of "
        "silently picking the more favorable one.",
        "Keep every list item short and specific (roughly 20 words or fewer).",
    ],
    output_schema_hint=(
        '{"why_now": str, "top_strengths": [str] (max 4), "top_risks": [str] (max 4), '
        '"conditions": [str] (max 3), "top_unknowns": [str] (max 4)}'
    ),
)


def _classify(
    weighted_score: float, overall_confidence: float, material_concerns: list[str]
) -> tuple[DecisionClass, bool]:
    if material_concerns:
        return DecisionClass.decline, True
    if weighted_score >= RECOMMEND_SCORE_THRESHOLD and overall_confidence >= RECOMMEND_CONFIDENCE_THRESHOLD:
        return DecisionClass.recommend, False
    if weighted_score >= MORE_RESEARCH_SCORE_FLOOR:
        return DecisionClass.more_research, False
    return DecisionClass.decline, False


async def run_decision(
    reports: dict[str, AnalysisReport],
    delegate: DelegateResult,
    tracker: UsageTracker,
    thesis_notes: str | None = None,
    progress=None,
) -> DecisionRecommendation:
    if progress is not None:
        progress.emit("decision", None, "started", detail="Synthesizing recommendation…")
    weighted_score = round(sum(reports[k].score * w for k, w in DIMENSION_WEIGHTS.items() if k in reports), 1)
    decision_class, hard_red_flag = _classify(weighted_score, delegate.overall_confidence, delegate.material_concerns)

    summary_lines = []
    for key, r in reports.items():
        risk_desc = [risk.description for risk in r.risks]
        summary_lines.append(
            f"{key}: score={r.score} confidence={r.confidence} recommendation={r.recommendation.value}\n"
            f"  strengths: {r.strengths}\n  risks: {risk_desc}\n  missing: {r.missing_information}"
        )

    user_prompt = (
        f"Weighted score (already computed, do not restate differently): {weighted_score}/10\n"
        f"Overall confidence (already computed): {delegate.overall_confidence}\n"
        f"Classification (already computed, do not change): {decision_class.value}\n"
        f"Material concerns flagged: {delegate.material_concerns or 'none'}\n"
        f"Analyst-provided fund thesis notes (context only, not evidence): {thesis_notes or 'none provided'}\n\n"
        "SPECIALIST REPORTS:\n" + "\n\n".join(summary_lines)
    )

    data = await llm_client.call_json(SYSTEM_PROMPT, user_prompt, label="decision", tracker=tracker, max_tokens=500)

    decision = DecisionRecommendation(
        decision_class=decision_class,
        weighted_score=weighted_score,
        overall_confidence=delegate.overall_confidence,
        hard_red_flag=hard_red_flag,
        **data,
    )
    if progress is not None:
        progress.emit("decision", None, "done", detail=decision_class.value)
    return decision
