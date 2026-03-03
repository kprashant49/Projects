def calculate_risk(evidence, sanctions_match, mobile=None, pan=None):

    score = 0

    # ---- Fraud / Adverse Media ----
    fraud_keywords = ["launder","fraud","scam","embezzle","BIFR","criminal","arrest","convict","terror","corrupt","investigate","regulator","penal","fine","police","charge","enforce","default","blacklist","discipline","court","litigate","politic","alleged","ponzi","insolvent","bankrupt","legal action","shell company","indict","tax evasion","bribe","prosecute","watch list","kickback","sanction","civil suit","misappropriate","insider trading","market manipulate","adverse media","debar","suspend","wilful","absconding","fugitive","offend","forge","false statement","misrepresent","consent","settle","money laundering"]

    fraud_hits = sum(
        1 for item in evidence
        if any(word in (item.get("snippet") or "").lower()
               for word in fraud_keywords)
    )

    fraud_score = min(fraud_hits * 10, 40)
    score += fraud_score

    # ---- Mobile Exposure ----
    mobile_hits = 0
    mobile_score = 0

    if mobile:
        mobile_hits = sum(
            1 for item in evidence
            if mobile in (item.get("snippet") or "")
        )
        mobile_score = 15 if mobile_hits > 0 else 0
        score += mobile_score

    # ---- PAN Exposure ----
    pan_hits = 0
    pan_score = 0

    if pan:
        pan_upper = pan.upper()
        pan_hits = sum(
            1 for item in evidence
            if pan_upper in (item.get("snippet") or "")
        )
        pan_score = 20 if pan_hits > 0 else 0
        score += pan_score

    # ---- Sanctions ----
    sanctions_score = 60 if sanctions_match else 0
    score += sanctions_score

    # ---- PEP (Myneta) ----
    pep_hits = sum(
        1 for item in evidence
        if item.get("source") == "Myneta"
    )

    pep_score = 20 if pep_hits > 0 else 0
    score += pep_score

    # Optional Cap
    score = min(score, 100)

    # ---- Risk Category ----
    if score >= 50:
        category = "High"
    elif score >= 35:
        category = "Medium"
    else:
        category = "Low"

    # ---- Breakdown Structure ----
    score_breakdown = {
        "fraud_hits": fraud_hits,
        "fraud_score": fraud_score,
        "sanctions_match": sanctions_match,
        "sanctions_score": sanctions_score,
        "pep_hits": pep_hits,
        "pep_score": pep_score,
        "mobile_hits": mobile_hits,
        "mobile_score": mobile_score,
        "pan_hits": pan_hits,
        "pan_score": pan_score,
        "total_score": score
    }

    return score, category, score_breakdown