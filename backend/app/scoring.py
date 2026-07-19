"""Fund-configurable scoring weights and decision thresholds (blueprint sections 12 and 14).

In a later version these move into an admin-editable scoring.yaml (FR-14). For v1 they are
a plain Python module so the whole pipeline has one obvious place to tune per fund thesis.
"""

DIMENSION_WEIGHTS = {
    "founder": 0.25,
    "market": 0.20,
    "product": 0.20,
    "competition": 0.15,
    "financial": 0.10,
    "risk": 0.10,
}

assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-6

RECOMMEND_SCORE_THRESHOLD = 7.5
RECOMMEND_CONFIDENCE_THRESHOLD = 0.75
MORE_RESEARCH_SCORE_FLOOR = 6.0
LOW_CONFIDENCE_THRESHOLD = 0.60
