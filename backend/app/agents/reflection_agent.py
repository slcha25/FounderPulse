"""Reflection Agent (blueprint stage 10) — stub for v1.

Real reflection needs a *verified* later outcome (next round, shutdown, revenue milestone —
section 22's "prevent memory contamination" rule), which does not exist at analysis time.
This file is the intended landing spot once outcome capture ships: it will diff the case's
reports/decision against the verified outcome and propose an Experience Memory entry that a
human must approve before it can influence future cases.
"""


def propose_reflection(case: dict, verified_outcome: dict) -> dict:
    raise NotImplementedError(
        "Reflection requires a verified outcome capture flow that does not exist yet in v1."
    )
