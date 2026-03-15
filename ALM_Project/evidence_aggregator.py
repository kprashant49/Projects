"""
evidence_aggregator.py — Collect and filter evidence for an AML subject.

Evidence sources (in order):
  1. SerpAPI Google search (general risk query)
  2. NewsAPI
  3. GNews
  4. Indian Kanoon — Selenium scraper (if USE_SELENIUM_INDIAN_KANOON) else Google site-search
  5. Myneta (PEP) — Selenium scraper (if USE_SELENIUM_MYNETA) else Google site-search

Design note — trusted vs general evidence
------------------------------------------
Results from domain-restricted site-searches (myneta.info, indiankanoon.org) are
already scoped to the subject by the quoted-name query, so they bypass the
name filter. They are also tagged with a normalised source label so that
downstream scoring (PEP hit detection in risk_scoring.py) reliably finds them
regardless of how SerpAPI formats the domain string.

General evidence (web, news) IS passed through the name filter to avoid
unrelated articles that happen to share common words with the query.
"""

from google_search import web_search
from news import news_search
from gnews import gnews_search
from dedupe import deduplicate_evidence
from name_matcher import is_evidence_match

from config import (
    USE_SELENIUM_INDIAN_KANOON,
    USE_SELENIUM_MYNETA,
    RISK_KEYWORDS,
)

# Normalised source labels used by risk_scoring.py for PEP / legal hit detection
_SOURCE_MYNETA  = "Myneta"
_SOURCE_KANOON  = "Indian Kanoon"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def collect_evidence(
    name: str,
    place: str,
    mobile: str | None = None,
    pan: str | None    = None,
) -> list[dict]:
    """
    Gather evidence from all configured sources, deduplicate, and return
    a filtered list of items plausibly related to the subject.
    """

    # ---- Build general search query ----
    base_query    = f"{name} {place}"
    mobile_clause = f'"{mobile}"'      if mobile else ""
    pan_clause    = f'"{pan.upper()}"' if pan    else ""
    risk_clause   = " OR ".join(RISK_KEYWORDS[:6])   # keep query length reasonable

    query = " ".join(p for p in [base_query, mobile_clause, pan_clause, risk_clause] if p).strip()

    # ---- General evidence (subject to name filter) ----
    general_evidence = []
    general_evidence += _safe("SerpAPI web search", web_search, query)
    general_evidence += _safe("NewsAPI",            news_search, query)
    general_evidence += _safe("GNews",              gnews_search, query)

    filtered_general = _filter_by_name(general_evidence, name)

    # ---- Trusted domain evidence (bypasses name filter, tagged with fixed source) ----
    trusted_evidence = []

    # Indian Kanoon
    if USE_SELENIUM_INDIAN_KANOON:
        from indian_kanoon import search_indian_kanoon
        kanoon_items = _safe("Indian Kanoon (Selenium)", search_indian_kanoon, name)
    else:
        kanoon_query = f'"{name}" site:indiankanoon.org'
        kanoon_items = _safe("Indian Kanoon (site-search)", web_search, kanoon_query)

    trusted_evidence += _tag_source(kanoon_items, _SOURCE_KANOON)

    # Myneta (PEP)
    if USE_SELENIUM_MYNETA:
        from myneta_search import search_myneta
        myneta_items = _safe("Myneta (Selenium)", search_myneta, name)
    else:
        myneta_query = f'"{name}" site:myneta.info'
        myneta_items = _safe("Myneta (site-search)", web_search, myneta_query)

    trusted_evidence += _tag_source(myneta_items, _SOURCE_MYNETA)

    # ---- Merge, deduplicate, return ----
    combined = filtered_general + trusted_evidence
    unique   = deduplicate_evidence(combined)

    print(f"[Evidence] General: {len(filtered_general)} | Trusted: {len(trusted_evidence)} | Total: {len(unique)}")
    return unique


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe(label: str, fn, *args) -> list[dict]:
    """Call fn(*args) and return its result; swallow exceptions with a log."""
    try:
        return fn(*args) or []
    except Exception as e:
        print(f"[Evidence] {label} failed: {e}")
        return []


def _tag_source(items: list[dict], source_label: str) -> list[dict]:
    """
    Overwrite the 'source' field with a normalised label.
    This ensures risk_scoring.py can reliably detect Myneta / Kanoon hits
    regardless of how SerpAPI or Selenium formats the domain string.
    """
    for item in items:
        item["source"] = source_label
    return items


def _filter_by_name(evidence: list[dict], name: str) -> list[dict]:
    """
    Keep only items whose title plausibly refers to the subject.
    Not applied to trusted domain results — those are already name-scoped
    by the quoted search query.
    """
    return [
        item for item in evidence
        if is_evidence_match(name, item.get("title", ""))
    ]