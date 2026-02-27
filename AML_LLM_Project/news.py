import requests


def news_search(query, api_key):

    if not api_key:
        print("News API key not provided — skipping News search.")
        return []

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "relevancy"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        evidence = []

        for article in data.get("articles", []):
            evidence.append({
                "source": "NewsAPI",
                "title": article.get("title"),
                "link": article.get("url"),
                "snippet": article.get("description") or ""
            })

        return evidence

    except requests.exceptions.HTTPError as e:
        print(f"News API HTTP error: {e}")
        return []

    except requests.exceptions.RequestException as e:
        print(f"News API request failed: {e}")
        return []

    except Exception as e:
        print(f"Unexpected News API error: {e}")
        return []