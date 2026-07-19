from ...schemas import StartupProfile
from ...clients.llm_client import UsageTracker
from .scanning_base import run_scanning_agent

MISSION = (
    "Evaluate the product: problem-solution evidence, technical feasibility, differentiation, "
    "maturity/traction and defensibility/moat."
)
SUBCRITERIA = [
    "problem-solution evidence (25%)",
    "feasibility (20%)",
    "differentiation (20%)",
    "maturity/traction (15%)",
    "defensibility/moat (20%)",
]


async def run(profile: StartupProfile, tracker: UsageTracker, progress=None):
    return await run_scanning_agent(
        agent_key="product",
        agent_label="Product Analysis Agent",
        mission=MISSION,
        subcriteria=SUBCRITERIA,
        profile=profile,
        tracker=tracker,
        progress=progress,
    )
