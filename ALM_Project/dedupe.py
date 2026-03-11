"""
dedupe.py — Remove duplicate evidence items.

Deduplication priority:
  1. Exact URL match (primary key) — catches same article from different APIs.
  2. Title + URL pair (fallback)   — catches minor URL variations.
"""


def deduplicate_evidence(evidence: list[dict]) -> list[dict]:
    seen_links  = set()
    seen_pairs  = set()
    unique      = []

    for item in evidence:
        link  = (item.get("link")  or "").strip().lower()
        title = (item.get("title") or "").strip().lower()

        # Primary: deduplicate purely on URL when one is available
        if link:
            if link in seen_links:
                continue
            seen_links.add(link)
        else:
            # Fallback for items with no URL (e.g. some scraped results)
            pair = (title, link)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

        unique.append(item)

    return unique
