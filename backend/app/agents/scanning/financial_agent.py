from ...schemas import StartupProfile
from ...clients.llm_client import UsageTracker
from .scanning_base import run_scanning_agent

MISSION = (
    "Evaluate financial health: revenue quality, growth, unit economics, runway/capital "
    "efficiency and reporting quality. Pre-seed/seed companies may have limited financial "
    "history — say so in missing_information rather than penalizing the score for it alone."
)
SUBCRITERIA = [
    "revenue quality (20%)",
    "growth (20%)",
    "unit economics (25%)",
    "runway/capital efficiency (20%)",
    "reporting quality (15%)",
]


async def run(profile: StartupProfile, tracker: UsageTracker, progress=None):
    return await run_scanning_agent(
        agent_key="financial",
        agent_label="Financial Analysis Agent",
        mission=MISSION,
        subcriteria=SUBCRITERIA,
        profile=profile,
        tracker=tracker,
        progress=progress,
    )
