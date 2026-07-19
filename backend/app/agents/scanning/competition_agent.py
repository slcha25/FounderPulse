from ...schemas import StartupProfile
from ...clients.llm_client import UsageTracker
from .scanning_base import run_scanning_agent

MISSION = (
    "Map the competitive landscape: differentiation, competitive intensity, entry barriers, "
    "positioning and durable advantage."
)
SUBCRITERIA = [
    "differentiation (25%)",
    "competitive intensity (20%)",
    "entry barriers (20%)",
    "positioning (20%)",
    "durable advantage (15%)",
]


async def run(profile: StartupProfile, tracker: UsageTracker, progress=None):
    return await run_scanning_agent(
        agent_key="competition",
        agent_label="Competition Analysis Agent",
        mission=MISSION,
        subcriteria=SUBCRITERIA,
        profile=profile,
        tracker=tracker,
        progress=progress,
    )
