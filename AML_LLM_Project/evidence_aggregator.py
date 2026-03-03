from google_search import web_search
from news import news_search
from gnews import gnews_search
from indian_kanoon import search_indian_kanoon
from myneta_search import search_myneta
import os
from dedupe import deduplicate_evidence
from rapidfuzz import fuzz
from name_matcher import is_strong_name_match

def collect_evidence(name, place, mobile=None, pan=None):
    # ---- Base Query ----
    base_query = f"{name} {place}"

    # ---- Optional Exact Match Fields ----
    mobile_query = f'"{mobile}"' if mobile else ""
    pan_query = f'"{pan.upper()}"' if pan else ""

    # ---- Risk Keywords ----
    risk_keywords = ["fraud","scam","criminal","default"]
    risk_terms = " OR ".join(risk_keywords)

    # ---- Final Query ----
    query_parts = [base_query, mobile_query, pan_query, risk_terms]
    query = " ".join(part for part in query_parts if part).strip()

    evidence = []

    # Serp
    evidence += web_search(query)

    # News
    try:
        evidence += news_search(query, os.getenv("NEWS_API_KEY"))
    except Exception as e:
        print("NewsAPI failed:", e)

    news_articles = gnews_search(query)
    evidence += news_articles

    # Indian Kanoon (wrapped safely)
    # try:
    #     kanoon_results = search_indian_kanoon(query)
    # except Exception as e:
    #     print(f"Indian Kanoon failed: {e}")
    #     kanoon_results = []

    kanoon_query = f'"{name}" site:indiankanoon.org'
    evidence += web_search(kanoon_query)

    # Myneta (PEP screening)
    # try:
    #     evidence += search_myneta(name)
    # except Exception as e:
    #     print("Myneta failed:", e)

    myneta_query = f'"{name}" site:myneta.info'
    evidence += web_search(myneta_query)

    # Normalize structure
    # for item in kanoon_results:
    #     evidence.append({
    #         "source": item.get("source"),
    #         "title": item.get("title"),
    #         "link": item.get("link"),
    #         "snippet": "Legal case reference from Indian Kanoon"
    #     })

    print(evidence)

    for item in evidence:
        if "myneta" in (item.get("source") or "").lower():
            print("Myneta Found:", item["title"])

    unique = deduplicate_evidence(evidence)
    filtered = filter_evidence_by_name(unique, name)

    print("Total before filter:", len(unique))
    print("Total after filter:", len(filtered))

    return filtered


def filter_evidence_by_name(evidence, name, place=None):
    filtered = []

    for item in evidence:
        title = item.get("title", "")
        snippet = (item.get("snippet") or "").lower()

        if is_strong_name_match(name, title):

            if place:
                if place.lower() in snippet:
                    filtered.append(item)
                else:
                    continue
            else:
                filtered.append(item)

    return filtered