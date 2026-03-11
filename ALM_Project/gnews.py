"""
gnews.py — News article search via the GNews API.
"""

import requests
from config import GNEWS_KEY


def gnews_search(query: str, max_results: int = 10) -> list[dict]:
    if not GNEWS_KEY:
        print("GNews API key not set — skipping GNews search.")
        return []

    url    = "https://gnews.io/api/v4/search"
    params = {
        "q":     query,
        "token": GNEWS_KEY,
        "lang":  "en",
        "max":   max_results,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])

        return [
            {
                "source":  article.get("source", {}).get("name", "GNews"),
                "title":   article.get("title", ""),
                "link":    article.get("url", ""),
                "snippet": article.get("description") or "",
            }
            for article in articles
        ]

    except Exception as e:
        print(f"GNews search failed: {e}")
        return []
