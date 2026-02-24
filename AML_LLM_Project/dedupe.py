def deduplicate_evidence(evidence):

    seen = set()
    unique = []

    for item in evidence:
        key = (
            item.get("title", "").strip().lower(),
            item.get("link", "").strip().lower()
        )

        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique