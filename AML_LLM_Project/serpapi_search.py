import os
import requests

def serpapi_search(query, engine="google", num=5):
    key = os.getenv("SERPAPI_KEY")
    if not key:
      raise ValueError("SERPAPI_KEY not set")



    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "engine": engine,
        "api_key": key,
        "num": num
    }
    resp = requests.get(url, params=params, timeout=10)

    resp.raise_for_status()

    return resp.json()