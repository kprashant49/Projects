"""
news.py — News article search via the NewsAPI.org v2 endpoint.
"""

import requests
from config import NEWS_API_KEY


def news_search(query: str) -> list[dict]:
    if not NEWS_API_KEY:
        print("NEWS_API_KEY not set — skipping NewsAPI search.")
        return []

    url    = "https://newsapi.org/v2/everything"
    params = {
        "q":        query,
        "apiKey":   NEWS_API_KEY,
        "language": "en",
        "sortBy":   "relevancy",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        return [
            {
                "source":  "NewsAPI",
                "title":   article.get("title", ""),
                "link":    article.get("url", ""),
                "snippet": article.get("description") or "",
            }
            for article in response.json().get("articles", [])
        ]

    except requests.exceptions.HTTPError as e:
        print(f"NewsAPI HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"NewsAPI request failed: {e}")
    except Exception as e:
        print(f"Unexpected NewsAPI error: {e}")

    return []
