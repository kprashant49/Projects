def calculate_risk(evidence, sanctions_match):

    score = 0

    fraud_hits = sum(
        1 for item in evidence
        if any(word in (item.get("snippet") or "").lower()
               for word in ["fraud", "scam", "money laundering"])
    )

    score += min(fraud_hits * 10, 40)

    if sanctions_match:
        score += 60

    pep_hits = sum(
        1 for item in evidence
        if item.get("source") == "Myneta"
    )

    if pep_hits > 0:
        score += 20

    if score >= 70:
        category = "High"
    elif score >= 40:
        category = "Medium"
    else:
        category = "Low"

    return score, category