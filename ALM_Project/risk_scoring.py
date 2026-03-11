"""
risk_scoring.py — Calculate an AML risk score from collected evidence.

All scoring weights and thresholds are defined in config.py so they can be
tuned without touching this file.
"""

import re
from config import (
    RISK_KEYWORDS,
    FRAUD_SCORE_PER_HIT,
    FRAUD_SCORE_MAX,
    SANCTIONS_SCORE,
    PEP_SCORE,
    MOBILE_SCORE,
    PAN_SCORE,
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
)

# Pre-compile keyword patterns once at import time (not inside the function)
_FRAUD_PATTERNS: list[re.Pattern] = []
for _word in RISK_KEYWORDS:
    _escaped = re.escape(_word.lower())
    if " " in _word:
        _pattern = r"\b" + _escaped.replace(r"\ ", r"\s+") + r"\b"
    else:
        _pattern = r"\b" + _escaped + r"\b"
    _FRAUD_PATTERNS.append(re.compile(_pattern, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_risk(
    evidence: list[dict],
    sanctions_match: bool,
    mobile: str | None = None,
    pan: str | None    = None,
) -> tuple[int, str, dict]:
    """
    Calculate a composite AML risk score.

    Returns:
        score     (int)  — 0–100 composite score.
        category  (str)  — 'High', 'Medium', or 'Low'.
        breakdown (dict) — per-component scores for reporting.
    """
    score = 0

    # ---- Fraud / Adverse Media ----
    fraud_hits = 0
    for item in evidence:
        text = (item.get("title", "") + " " + item.get("snippet", "")).lower()
        for pattern in _FRAUD_PATTERNS:
            if pattern.search(text):
                fraud_hits += 1
                break  # count each article at most once

    fraud_score = min(fraud_hits * FRAUD_SCORE_PER_HIT, FRAUD_SCORE_MAX)
    score += fraud_score

    # ---- Sanctions ----
    sanctions_score = SANCTIONS_SCORE if sanctions_match else 0
    score += sanctions_score

    # ---- PEP (Myneta hits) ----
    pep_hits = sum(
        1 for item in evidence
        if "myneta" in (item.get("source") or "").lower()
    )
    pep_score = PEP_SCORE if pep_hits > 0 else 0
    score += pep_score

    # ---- Mobile Exposure ----
    mobile_hits  = 0
    mobile_score = 0
    if mobile:
        mobile_hits  = sum(1 for item in evidence if mobile in (item.get("snippet") or ""))
        mobile_score = MOBILE_SCORE if mobile_hits > 0 else 0
        score += mobile_score

    # ---- PAN Exposure ----
    pan_hits  = 0
    pan_score = 0
    if pan:
        pan_upper = pan.upper()
        pan_hits  = sum(1 for item in evidence if pan_upper in (item.get("snippet") or ""))
        pan_score = PAN_SCORE if pan_hits > 0 else 0
        score += pan_score

    # ---- Cap & log if truncated ----
    raw_score = score
    score     = min(score, 100)
    if raw_score > 100:
        print(f"[Risk] Score capped at 100 (raw={raw_score})")

    # ---- Risk Category ----
    if score >= RISK_HIGH_THRESHOLD:
        category = "High"
    elif score >= RISK_MEDIUM_THRESHOLD:
        category = "Medium"
    else:
        category = "Low"

    breakdown = {
        "fraud_hits":       fraud_hits,
        "fraud_score":      fraud_score,
        "sanctions_match":  sanctions_match,
        "sanctions_score":  sanctions_score,
        "pep_hits":         pep_hits,
        "pep_score":        pep_score,
        "mobile_hits":      mobile_hits,
        "mobile_score":     mobile_score,
        "pan_hits":         pan_hits,
        "pan_score":        pan_score,
        "total_score":      score,
    }

    return score, category, breakdown
