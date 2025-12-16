def levenshtein_distance(a: str, b: str) -> int:
    a = a or ""
    b = b or ""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n

    previous = list(range(m + 1))
    for i, ca in enumerate(a, start=1):
        current = [i] + [0] * m
        for j, cb in enumerate(b, start=1):
            insert_cost = previous[j] + 1
            delete_cost = current[j-1] + 1
            replace_cost = previous[j-1] + (0 if ca == cb else 1)
            current[j] = min(insert_cost, delete_cost, replace_cost)
        previous = current

    return previous[m]

def simple_ratio(a: str, b: str) -> float:
    a = a.strip().lower()
    b = b.strip().lower()
    if not a and not b:
        return 100.0

    dist = levenshtein_distance(a, b)
    max_len = max(len(a), len(b))
    return round((1 - dist / max_len) * 100, 2)

def _tokens(text: str):
    return [t for t in text.lower().strip().split() if t]

def token_sort_ratio(a: str, b: str) -> float:
    at = " ".join(sorted(_tokens(a)))
    bt = " ".join(sorted(_tokens(b)))
    return simple_ratio(at, bt)

def token_set_ratio(a: str, b: str) -> float:
    atoks = set(_tokens(a))
    btoks = set(_tokens(b))

    common = " ".join(sorted(atoks & btoks))
    diff_a = " ".join(sorted(atoks - btoks))
    diff_b = " ".join(sorted(btoks - atoks))

    candidates = []
    if common:
        candidates.append(simple_ratio(common, common))

    candidates.append(simple_ratio((common + " " + diff_a).strip(),
                                   (common + " " + diff_b).strip()))

    candidates.append(simple_ratio(a, b))
    return max(candidates)

def partial_ratio(a: str, b: str) -> float:
    a = a.strip().lower()
    b = b.strip().lower()

    if len(a) <= len(b):
        short, long = a, b
    else:
        short, long = b, a

    best = 0.0
    for i in range(len(long) - len(short) + 1):
        segment = long[i:i+len(short)]
        score = simple_ratio(short, segment)
        best = max(best, score)

    return best

def combined_score(a: str, b: str):
    return {
        "simple_ratio": simple_ratio(a, b),
        "partial_ratio": partial_ratio(a, b),
        "token_sort_ratio": token_sort_ratio(a, b),
        "token_set_ratio": token_set_ratio(a, b),
    }

def decide_match(a: str, b: str, threshold=85):
    scores = combined_score(a, b)
    deciding = max(scores["token_set_ratio"], scores["partial_ratio"])
    return deciding >= threshold, deciding, scores

def main():
    print("Fuzzy Name Matcher, please provide names to match.")
    a = input("Enter first name: ")
    b = input("Enter second name: ")

    match, deciding, scores = decide_match(a, b)

    print("\n--- Scores ---")
    for k, v in scores.items():
        print(f"{k}: {v}")

    print(f"\nDeciding score: {deciding}")
    print("Match:", "YES" if match else "NO")

if __name__ == "__main__":
    main()
