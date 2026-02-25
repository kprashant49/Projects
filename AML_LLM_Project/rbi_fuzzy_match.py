from rapidfuzz import fuzz

def fuzzy_match_name(name, list_of_names):

    matches = []

    for entry in list_of_names:
        score = fuzz.token_sort_ratio(name.lower(), entry.lower())

        if score > 85:
            matches.append((entry, score))

    return matches