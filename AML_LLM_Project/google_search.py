from serpapi_search import serpapi_search

def web_search(query):
    results = serpapi_search(query, engine="google", num=5)

    output = []

    for item in results.get("organic_results", []):

        source_field = item.get("source")

        if isinstance(source_field, dict):
            source_value = source_field.get("domain", "")
        elif isinstance(source_field, str):
            source_value = source_field
        else:
            source_value = ""

        output.append({
            "source": source_value,
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet") or ""
        })

    return output