"""Delegate Agent (blueprint stage 6): checks coverage/conflicts, no LLM call in v1.

The full blueprint has Delegate spin up another Tavily+LLM research round when confidence is
low (FR-08). For v1 that loop is deliberately cut to control cost and latency: instead this
agent computes the numbers deterministically and passes every flagged gap straight into the
memo's diligence-plan section for the human reviewer to action within the 24h SLA. See README
"Known v1 simplifications" for the plan to add the real research loop back.
"""

from ..schemas import AnalysisReport, DelegateResult
from ..scoring import DIMENSION_WEIGHTS, LOW_CONFIDENCE_THRESHOLD


def run_delegate(reports: dict[str, AnalysisReport], progress=None) -> DelegateResult:
    if progress is not None:
        progress.emit("delegate", None, "started", detail="Checking evidence coverage and conflicts…")
    overall_confidence = sum(reports[k].confidence * w for k, w in DIMENSION_WEIGHTS.items() if k in reports)

    material_concerns = [k for k, r in reports.items() if r.recommendation == "material_concern"]
    low_confidence = [k for k, r in reports.items() if r.confidence < LOW_CONFIDENCE_THRESHOLD]

    missing: list[str] = []
    for r in reports.values():
        for item in r.missing_information:
            if item not in missing:
                missing.append(item)

    result = DelegateResult(
        overall_confidence=round(overall_confidence, 2),
        material_concerns=material_concerns,
        low_confidence_dimensions=low_confidence,
        missing_information=missing[:10],
        can_proceed=True,
    )
    if progress is not None:
        progress.emit(
            "delegate", None, "done",
            detail=f"overall confidence {result.overall_confidence:.2f}, {len(missing)} open gaps flagged",
        )
    return result
