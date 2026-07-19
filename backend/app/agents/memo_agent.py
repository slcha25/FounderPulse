"""Memo Agent (blueprint stage 8): renders the decision package as an editable IC memo.

Pure Python templating — no LLM call. Every structured field already came from a cited agent
output, so re-generating prose here would only add cost and hallucination risk for no benefit.
Follows the Appendix A section list. Section 13 (Human Decision) is always left pending: this
agent must never fill in Accept/Reject itself (FR-11 human gate).
"""

from ..schemas import AnalysisReport, DecisionRecommendation, DelegateResult, EvidenceRecord, StartupProfile

AGENT_LABELS = {
    "founder": "Founder & Team",
    "market": "Market",
    "product": "Product & Technology",
    "competition": "Competition",
    "financial": "Business & Financials",
    "risk": "Risk Resilience",
}

SECTION_ORDER = ["founder", "market", "product", "competition", "financial", "risk"]


def _report_section(key: str, report: AnalysisReport) -> str:
    strengths = "\n".join(f"  - {s}" for s in report.strengths) or "  - none flagged"
    risks = "\n".join(f"  - [{r.severity.upper()}] {r.description}" for r in report.risks) or "  - none flagged"
    missing = "\n".join(f"  - {m}" for m in report.missing_information) or "  - none flagged"
    return (
        f"### {AGENT_LABELS.get(key, key.title())}\n"
        f"**Score:** {report.score}/10  **Confidence:** {report.confidence:.2f}  "
        f"**Recommendation:** {report.recommendation.value}\n\n"
        f"Strengths:\n{strengths}\n\nRisks:\n{risks}\n\nMissing information:\n{missing}\n\n"
        f"Sensitivity: {report.sensitivity or 'not provided'}\n\n"
        f"Evidence for: {', '.join(report.evidence_for) or 'none'} | "
        f"Evidence against: {', '.join(report.evidence_against) or 'none'}\n"
    )


def render_memo(
    profile: StartupProfile,
    reports: dict[str, AnalysisReport],
    delegate: DelegateResult,
    decision: DecisionRecommendation,
    evidence: list[EvidenceRecord],
    decision_due_at: str,
    progress=None,
) -> str:
    if progress is not None:
        progress.emit("memo", None, "started", detail="Rendering investment memo…")
    strengths = "\n".join(f"- {s}" for s in decision.top_strengths) or "- none"
    risks = "\n".join(f"- {r}" for r in decision.top_risks) or "- none"
    conditions = "\n".join(f"- {c}" for c in decision.conditions) or "- none"
    unknowns = "\n".join(f"- {u}" for u in decision.top_unknowns) or "- none"
    diligence_plan = "\n".join(f"- {m}" for m in delegate.missing_information) or "- no open items flagged"
    evidence_table = "\n".join(
        f"| {e.evidence_id} | {e.source_type} | {e.title} | {e.url} |" for e in evidence
    ) or "| - | - | no evidence recorded | - |"
    sensitivity_lines = "\n".join(
        f"- **{AGENT_LABELS.get(k, k)}:** {reports[k].sensitivity}"
        for k in SECTION_ORDER
        if k in reports and reports[k].sensitivity
    ) or "- none provided"
    report_sections = "\n".join(_report_section(k, reports[k]) for k in SECTION_ORDER if k in reports)

    if progress is not None:
        progress.emit("memo", None, "done", detail="Memo ready")

    return f"""# Investment Memo — {profile.company_name}

## 1. Recommendation
**Class:** {decision.decision_class.value}
**Weighted score:** {decision.weighted_score}/10
**Overall confidence:** {decision.overall_confidence:.2f}
**Rationale:** {decision.why_now}
**Hard red flag triggered:** {"Yes" if decision.hard_red_flag else "No"}

> This is decision-support advice only. Final Accept/Reject authority belongs to an authorized human reviewer.

## 2. Company Snapshot
- **One-liner:** {profile.one_liner or "unknown"}
- **Stage:** {profile.stage or "unknown"}  |  **Sector:** {profile.sector or "unknown"}
- **Website:** {profile.company_url or "unknown"}
- **Founders:** {", ".join(profile.founders) or "unknown"}

## 3. Investment Thesis
{decision.why_now}

## 4-9. Specialist Analysis
{report_sections}

## 10. Diligence Plan (open items for human follow-up)
{diligence_plan}

## 11. Decision Sensitivity
{sensitivity_lines}

## 12. Evidence Appendix
| ID | Source type | Title | URL |
|---|---|---|---|
{evidence_table}

## 13. Human Decision
- **Outcome:** _pending human review_
- **Reason code:** _pending_
- **Rationale:** _pending_
- **Reviewer:** _pending_
- **Decided at:** _pending_
- **Decision due at (24h SLA):** {decision_due_at}
- **Deadline met:** _pending_

---
### Top strengths across reports
{strengths}

### Top risks across reports
{risks}

### Conditions before proceeding
{conditions}

### Top unknowns
{unknowns}
"""
