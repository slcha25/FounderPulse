"""Source Agents (blueprint stage 3): collect permitted evidence, no analysis or opinions.

For v1 this runs a fixed set of targeted Tavily searches per case (cheaper and more predictable
than letting an LLM decide what to search) plus one page extract of the company's own site.
"""

import asyncio

from ..clients import tavily_client
from ..schemas import EvidenceRecord

QUERY_TEMPLATES = [
    ("company_overview", "{name} startup company overview what they do"),
    ("founders", "{name} founders CEO co-founder background LinkedIn"),
    ("funding", "{name} funding round investors valuation raised"),
    ("market_competition", "{name} competitors alternatives market"),
    ("traction", "{name} customers users traction reviews growth"),
]

MAX_RESULTS_PER_QUERY = 4
EXCERPT_CHARS = 500
HOMEPAGE_CHARS = 800


def evidence_from_uploads(uploaded_docs: list[tuple[str, str]], start_counter: int) -> list[EvidenceRecord]:
    """uploaded_docs: list of (filename, extracted_text). See document_parser.extract_text."""
    evidence: list[EvidenceRecord] = []
    counter = start_counter
    retrieved_at = tavily_client.now_iso()
    for filename, text in uploaded_docs:
        if not text.strip():
            continue
        evidence.append(
            EvidenceRecord(
                evidence_id=f"e{counter}",
                claim_context="uploaded_document",
                title=filename,
                url=f"upload://{filename}",
                source_type="first_party",
                excerpt=text,
                retrieved_at=retrieved_at,
            )
        )
        counter += 1
    return evidence


async def gather_evidence(company_name: str, company_url: str | None = None, progress=None) -> list[EvidenceRecord]:
    if progress is not None:
        progress.emit("sources", None, "started", detail="Searching web, funding databases and company site…")
    tasks = []
    labels = []
    for claim_context, template in QUERY_TEMPLATES:
        tasks.append(tavily_client.search(template.format(name=company_name), max_results=MAX_RESULTS_PER_QUERY))
        labels.append(claim_context)

    if company_url:
        tasks.append(tavily_client.extract(company_url))
        labels.append("homepage")

    results = await asyncio.gather(*tasks, return_exceptions=True)

    evidence: list[EvidenceRecord] = []
    counter = 1
    retrieved_at = tavily_client.now_iso()

    for label, result in zip(labels, results):
        if isinstance(result, Exception):
            continue

        if label == "homepage":
            if result:
                evidence.append(
                    EvidenceRecord(
                        evidence_id=f"e{counter}",
                        claim_context="homepage",
                        title=f"{company_name} official website",
                        url=company_url or "",
                        source_type="first_party",
                        excerpt=result[:HOMEPAGE_CHARS],
                        retrieved_at=retrieved_at,
                    )
                )
                counter += 1
            continue

        for item in result:
            excerpt = (item.get("content") or "")[:EXCERPT_CHARS]
            if not excerpt:
                continue
            evidence.append(
                EvidenceRecord(
                    evidence_id=f"e{counter}",
                    claim_context=label,
                    title=(item.get("title") or "")[:200],
                    url=item.get("url", ""),
                    source_type="independent_secondary",
                    excerpt=excerpt,
                    published_date=item.get("published_date"),
                    retrieved_at=retrieved_at,
                )
            )
            counter += 1

    if progress is not None:
        progress.emit("sources", None, "done", detail=f"{len(evidence)} evidence records collected")
    return evidence
