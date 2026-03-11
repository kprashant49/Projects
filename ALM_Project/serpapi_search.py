"""
serpapi_search.py — Thin wrapper around the SerpAPI HTTP endpoint.
"""

import requests
from config import SERPAPI_KEY, SEARCH_RESULTS_PER_QUERY


def serpapi_search(query: str, engine: str = "google", num: int = SEARCH_RESULTS_PER_QUERY) -> dict:
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY is not set. Check your .env file.")

    url = "https://serpapi.com/search.json"
    params = {
        "q":       query,
        "engine":  engine,
        "api_key": SERPAPI_KEY,
        "num":     num,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()
