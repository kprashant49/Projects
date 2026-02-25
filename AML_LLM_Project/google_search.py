import requests

def google_search(query, api_key, cx, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": num_results
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    results = response.json()

    evidence = []

    for item in results.get("items", []):
        evidence.append({
            "source": "Google",
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return evidence