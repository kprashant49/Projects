# from serpapi import GoogleSearch
#
# params = {
#   "api_key": "4c9d281a9a6a0b500e84dee5c7299e9d3cef5756e7323f746747545074f5a41e",
#   "engine": "google",
#   "google_domain": "google.com",
#   "q": "Coffee"
# }
#
# search = GoogleSearch(params)
# results = search.get_dict()


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
    resp = requests.get(url, params=params)

    resp.raise_for_status()

    return resp.json()