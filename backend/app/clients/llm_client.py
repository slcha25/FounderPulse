import json

from openai import AsyncOpenAI

from .. import config

_client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

# Approx gpt-4o-mini pricing per 1M tokens, used only for the in-app cost estimate shown to the reviewer.
_PRICE_PER_1M_INPUT = 0.15
_PRICE_PER_1M_OUTPUT = 0.60


class UsageTracker:
    """Accumulates token usage across every LLM call in one case run (blueprint section 28: cost governance)."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def record(self, label: str, usage) -> None:
        self.calls.append(
            {
                "label": label,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }
        )

    def summary(self) -> dict:
        total_prompt = sum(c["prompt_tokens"] for c in self.calls)
        total_completion = sum(c["completion_tokens"] for c in self.calls)
        est_cost = (total_prompt / 1_000_000 * _PRICE_PER_1M_INPUT) + (
            total_completion / 1_000_000 * _PRICE_PER_1M_OUTPUT
        )
        return {
            "model": config.LLM_MODEL,
            "llm_calls": self.calls,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "estimated_cost_usd": round(est_cost, 5),
        }


async def call_json(
    system_prompt: str,
    user_prompt: str,
    *,
    label: str,
    tracker: UsageTracker | None = None,
    max_tokens: int = 600,
    temperature: float = 0.2,
) -> dict:
    response = await _client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if tracker is not None:
        tracker.record(label, response.usage)
    content = response.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label}: model did not return valid JSON: {content[:200]}") from exc
