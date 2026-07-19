from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    evidence_id: str
    claim_context: str
    title: str
    url: str
    source_type: str
    excerpt: str
    published_date: Optional[str] = None
    retrieved_at: str


class StartupProfile(BaseModel):
    company_name: str
    company_url: Optional[str] = None
    one_liner: Optional[str] = None
    stage: Optional[str] = None
    sector: Optional[str] = None
    founders: list[str] = Field(default_factory=list)
    product_summary: Optional[str] = None
    market_summary: Optional[str] = None
    competition_summary: Optional[str] = None
    traction_summary: Optional[str] = None
    financing_summary: Optional[str] = None
    claims: list[dict] = Field(default_factory=list)
    profile_version: int = 1


class RiskItem(BaseModel):
    description: str
    severity: str = "medium"
    likelihood: Optional[str] = None


class Recommendation(str, Enum):
    pass_to_decision = "pass_to_decision"
    need_more_research = "need_more_research"
    material_concern = "material_concern"


class AnalysisReport(BaseModel):
    agent: str
    score: float
    confidence: float
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[RiskItem] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommendation: Recommendation
    sensitivity: Optional[str] = None


class DelegateResult(BaseModel):
    overall_confidence: float
    material_concerns: list[str] = Field(default_factory=list)
    low_confidence_dimensions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    can_proceed: bool = True


class DecisionClass(str, Enum):
    recommend = "Recommend for IC Review"
    more_research = "More Research"
    decline = "Decline / Watchlist"


class DecisionRecommendation(BaseModel):
    decision_class: DecisionClass
    weighted_score: float
    overall_confidence: float
    why_now: str
    top_strengths: list[str] = Field(default_factory=list)
    top_risks: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    top_unknowns: list[str] = Field(default_factory=list)
    hard_red_flag: bool = False


class HumanDecision(BaseModel):
    outcome: str
    reason_code: Optional[str] = None
    rationale: str
    reviewer: str
    decided_at: str
    deadline_met: Optional[bool] = None
    override: bool = False


class CaseRecord(BaseModel):
    case_id: str
    company_name: str
    company_url: Optional[str] = None
    stage: Optional[str] = None
    sector: Optional[str] = None
    thesis_notes: Optional[str] = None
    created_at: str
    application_validated_at: str
    decision_due_at: str
    profile: StartupProfile
    evidence: list[EvidenceRecord]
    reports: dict[str, AnalysisReport]
    delegate: DelegateResult
    decision: DecisionRecommendation
    memo_markdown: str
    human_decision: Optional[HumanDecision] = None
    cost_summary: dict = Field(default_factory=dict)


class ContactMessage(BaseModel):
    message_id: str
    name: str
    email: str
    message: str
    submitted_at: str
