def news_search(query, api_key = "bf8c3fac5ce145dc912629da6dae38aa"):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "apiKey": api_key,
        "language": "en",
        "sortBy": "relevancy"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    evidence = []

    for article in data.get("articles", []):
        evidence.append({
            "source": "NewsAPI",
            "title": article.get("title"),
            "link": article.get("url"),
            "snippet": article.get("description")
        })

    return evidence