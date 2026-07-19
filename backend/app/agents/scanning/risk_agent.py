from ...schemas import StartupProfile
from ...clients.llm_client import UsageTracker
from .scanning_base import run_scanning_agent

MISSION = (
    "Identify risk scenarios across market, execution, technology, financial, legal/compliance "
    "and concentration risk. IMPORTANT: unlike the other five agents, a HIGH score here means "
    "risk is well understood and controlled — a LOW score means risk is severe or unmitigated. "
    "List each concrete risk in risks[] regardless of the overall score."
)
SUBCRITERIA = [
    "market risk",
    "execution risk",
    "technology risk",
    "financial risk",
    "legal/compliance risk",
    "concentration risk",
]


async def run(profile: StartupProfile, tracker: UsageTracker, progress=None):
    return await run_scanning_agent(
        agent_key="risk",
        agent_label="Risk Analysis Agent",
        mission=MISSION,
        subcriteria=SUBCRITERIA,
        profile=profile,
        tracker=tracker,
        progress=progress,
    )
