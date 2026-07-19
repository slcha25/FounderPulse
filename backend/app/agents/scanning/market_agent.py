from ...schemas import StartupProfile
from ...clients.llm_client import UsageTracker
from .scanning_base import run_scanning_agent

MISSION = (
    "Evaluate the market opportunity: addressable need, growth/tailwinds, pain/urgency, "
    "reachable segment and willingness to pay."
)
SUBCRITERIA = [
    "addressable need (25%)",
    "growth/tailwinds (20%)",
    "pain/urgency (20%)",
    "reachable segment (20%)",
    "willingness to pay (15%)",
]


async def run(profile: StartupProfile, tracker: UsageTracker, progress=None):
    return await run_scanning_agent(
        agent_key="market",
        agent_label="Market Analysis Agent",
        mission=MISSION,
        subcriteria=SUBCRITERIA,
        profile=profile,
        tracker=tracker,
        progress=progress,
    )
