"""
evidence_aggregator.py — Collect and filter evidence for an AML subject.

Evidence sources (in order):
  1. SerpAPI Google search (general risk query)
  2. NewsAPI
  3. GNews
  4. Indian Kanoon — Selenium scraper (if USE_SELENIUM_INDIAN_KANOON) else Google site-search
  5. Myneta (PEP) — Selenium scraper (if USE_SELENIUM_MYNETA) else Google site-search
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
    Gather evidence from all configured sources, deduplicate, and filter
    to items that plausibly refer to the subject by name.
    """
    evidence = []

    # ---- Build search query ----
    base_query    = f"{name} {place}"
    mobile_clause = f'"{mobile}"'  if mobile  else ""
    pan_clause    = f'"{pan.upper()}"' if pan   else ""
    risk_clause   = " OR ".join(RISK_KEYWORDS[:6])             # keep query short

    query_parts   = [base_query, mobile_clause, pan_clause, risk_clause]
    query         = " ".join(p for p in query_parts if p).strip()

    # ---- 1. General web search ----
    evidence += _safe("SerpAPI web search", web_search, query)

    # ---- 2. NewsAPI ----
    evidence += _safe("NewsAPI", news_search, query)

    # ---- 3. GNews ----
    evidence += _safe("GNews", gnews_search, query)

    # ---- 4. Indian Kanoon ----
    if USE_SELENIUM_INDIAN_KANOON:
        from indian_kanoon import search_indian_kanoon
        evidence += _safe("Indian Kanoon (Selenium)", search_indian_kanoon, name)
    else:
        kanoon_query = f'"{name}" site:indiankanoon.org'
        evidence += _safe("Indian Kanoon (site-search)", web_search, kanoon_query)

    # ---- 5. Myneta (PEP) ----
    if USE_SELENIUM_MYNETA:
        from myneta_search import search_myneta
        evidence += _safe("Myneta (Selenium)", search_myneta, name)
    else:
        myneta_query = f'"{name}" site:myneta.info'
        evidence += _safe("Myneta (site-search)", web_search, myneta_query)

    # ---- Post-process ----
    unique   = deduplicate_evidence(evidence)
    filtered = _filter_by_name(unique, name)

    return filtered


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


def _filter_by_name(evidence: list[dict], name: str) -> list[dict]:
    """
    Keep only evidence items whose title plausibly matches the subject's name.
    Matching logic is delegated entirely to name_matcher.is_evidence_match.
    """
    return [
        item for item in evidence
        if is_evidence_match(name, item.get("title", ""))
    ]
