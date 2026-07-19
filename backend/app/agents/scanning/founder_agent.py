from ...schemas import StartupProfile
from ...clients.llm_client import UsageTracker
from .scanning_base import run_scanning_agent

MISSION = (
    "Evaluate the founding team: relevant startup experience, domain expertise, "
    "technical/professional capability, leadership/team-building and execution evidence."
)
SUBCRITERIA = [
    "relevant startup experience (25%)",
    "domain experience (20%)",
    "technical/professional capability (20%)",
    "leadership and team-building (20%)",
    "execution evidence (15%)",
]


async def run(profile: StartupProfile, tracker: UsageTracker, progress=None):
    return await run_scanning_agent(
        agent_key="founder",
        agent_label="Founder Analysis Agent",
        mission=MISSION,
        subcriteria=SUBCRITERIA,
        profile=profile,
        tracker=tracker,
        progress=progress,
    )
