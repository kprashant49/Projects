from rapidfuzz import fuzz


def normalize_name(name: str):
    return name.lower().strip().replace(".", "")


def split_name(name: str):
    parts = normalize_name(name).split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[-1]


def is_strong_name_match(input_name, candidate_name):

    input_n = input_name.lower().strip()
    candidate_n = candidate_name.lower().strip()

    full_similarity = fuzz.token_sort_ratio(input_n, candidate_n)
    partial_similarity = fuzz.partial_ratio(input_n, candidate_n)

    # Exact or near exact
    if full_similarity >= 60:
        return True

    # Allow minor spelling errors
    if partial_similarity >= 62:
        return True

    # First + Last name contained
    if input_n in candidate_n:
        return True

    return False