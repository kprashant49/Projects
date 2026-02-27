import os
import requests


def gnews_search(query, max_results=10):
    key = os.getenv("GNEWS_KEY")

    if not key:
        print("GNews API key not set — skipping.")
        return []

    url = "https://gnews.io/api/v4/search"

    params = {
        "q": query,
        "token": key,
        "lang": "en",
        "max": max_results
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("articles", [])

        output = []
        for article in data:
            output.append({
                "source": article.get("source", {}).get("name", "GNews"),
                "title": article.get("title"),
                "link": article.get("url"),
                "snippet": article.get("description") or ""
            })

        return output

    except Exception as e:
        print(f"GNews search failed: {e}")
        return []