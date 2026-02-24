from google import google_search
from news import news_search
from indian_kanoon import search_indian_kanoon
import os
from dedupe import deduplicate_evidence


def collect_evidence(name, place):

    query = f"{name} {place} fraud OR scam OR criminal OR default"

    evidence = []

    # Google
    evidence += google_search(
        query,
        os.getenv("GOOGLE_KEY"),
        os.getenv("GOOGLE_CX")
    )

    # News
    evidence += news_search(
        query,
        os.getenv("NEWS_API_KEY")
    )

    # Indian Kanoon (wrapped safely)
    try:
        kanoon_results = search_indian_kanoon(query)
    except Exception as e:
        print(f"Indian Kanoon failed: {e}")
        kanoon_results = []

    # Normalize structure
    for item in kanoon_results:
        evidence.append({
            "source": item.get("source"),
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": "Legal case reference from Indian Kanoon"
        })

    return deduplicate_evidence(evidence)