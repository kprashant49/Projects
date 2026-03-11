"""
name_matcher.py — Single source of truth for all name-matching logic.

Covers three distinct use cases, each with appropriate thresholds:
  1. Evidence filtering  — match a subject's name against article titles/snippets.
  2. Sanctions screening — match against UN/RBI sanctions list entries.
  3. PEP screening       — match against Myneta politician names.

Why multiple strategies?
  Standard fuzzy ratios struggle with 4-5 word names because:
  - Token order can vary (e.g. "Abdul Rahman Al Hussain Mohammed").
  - Middle names may be omitted or abbreviated in one source.
  - Common tokens like "Mohammed" or "Singh" appear in many unrelated names.
  The approach below layers several signals and requires meaningful token overlap
  for long names, which dramatically reduces false positives.
"""

import re
from rapidfuzz import fuzz
from config import (
    EVIDENCE_FILTER_TOKEN_SORT_THRESHOLD,
    EVIDENCE_FILTER_PARTIAL_RATIO_THRESHOLD,
    EVIDENCE_FILTER_TOKEN_OVERLAP_RATIO,
    SANCTIONS_FULL_MATCH_THRESHOLD,
    SANCTIONS_SET_RATIO_THRESHOLD,
    PEP_MATCH_THRESHOLD,
    MIN_MEANINGFUL_TOKEN_LENGTH,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Tokens that add noise in multi-word names (titles, common prefixes, etc.)
_STOP_TOKENS = {
    "mr", "mrs", "ms", "dr", "prof", "sh", "shri", "smt",
    "al", "bin", "binti", "bt", "a", "s", "m",
}


def normalize_name(name: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    name = name.lower().strip()
    name = re.sub(r"[.\-,]", " ", name)       # replace punctuation with space
    name = re.sub(r"\s+", " ", name).strip()   # collapse multiple spaces
    return name


def _meaningful_tokens(name: str) -> list[str]:
    """Return tokens that are long enough and not stop-words."""
    return [
        t for t in normalize_name(name).split()
        if len(t) >= MIN_MEANINGFUL_TOKEN_LENGTH and t not in _STOP_TOKENS
    ]


def _token_overlap_ratio(name_a: str, name_b: str) -> float:
    """
    Fraction of meaningful tokens in name_a that appear verbatim in name_b.
    Useful for long names: if 4 of 5 tokens match, it is almost certainly the
    same person regardless of ordering or extra words.
    """
    tokens_a = _meaningful_tokens(name_a)
    tokens_b = set(normalize_name(name_b).split())

    if not tokens_a:
        return 0.0

    matched = sum(1 for t in tokens_a if t in tokens_b)
    return matched / len(tokens_a)


def _first_last_match(name_a: str, name_b: str) -> bool:
    """
    True when both the first and last meaningful tokens of name_a
    appear somewhere in name_b. Handles cases like
    'Mohammed Abdul Rahman' matching 'Mohammed ... Rahman'.
    Guard: tokens must be at least MIN_MEANINGFUL_TOKEN_LENGTH chars.
    """
    tokens = _meaningful_tokens(name_a)
    if len(tokens) < 2:
        return False

    first, last = tokens[0], tokens[-1]
    b_norm = normalize_name(name_b)

    # Require both are long enough to be distinctive
    if len(first) < MIN_MEANINGFUL_TOKEN_LENGTH or len(last) < MIN_MEANINGFUL_TOKEN_LENGTH:
        return False

    return first in b_norm and last in b_norm


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_evidence_match(input_name: str, candidate_text: str) -> bool:
    """
    Determines whether candidate_text (an article title or snippet) likely
    refers to input_name. Designed for recall: we would rather keep an extra
    article than miss a relevant one.

    Handles:
    - Full name matches with word order variations (token_sort_ratio).
    - Name appearing inside a longer headline (partial_ratio).
    - 4-5 word names where only a subset of tokens appear (token_overlap).
    - First + last name appearing anywhere in the text.
    """
    a = normalize_name(input_name)
    b = candidate_text.lower().strip()

    # 1. Token sort — robust to word-order differences
    if fuzz.token_sort_ratio(a, b) >= EVIDENCE_FILTER_TOKEN_SORT_THRESHOLD:
        return True

    # 2. Partial ratio — name appears as a substring of a longer title
    #    Guard: input must be non-trivially short to avoid single-word explosions
    if len(a) >= 6 and fuzz.partial_ratio(a, b) >= EVIDENCE_FILTER_PARTIAL_RATIO_THRESHOLD:
        return True

    # 3. Token set ratio — input name tokens are a subset of candidate tokens
    #    Good for "Abdul Rahman" matching "Dr. Abdul Karim Rahman"
    if fuzz.token_set_ratio(a, b) >= EVIDENCE_FILTER_PARTIAL_RATIO_THRESHOLD:
        return True

    # 4. Multi-word overlap — for 3+ word names, most tokens must appear verbatim
    tokens_a = a.split()
    if len(tokens_a) >= 3:
        if _token_overlap_ratio(a, b) >= EVIDENCE_FILTER_TOKEN_OVERLAP_RATIO:
            return True

    # 5. First + last name check — the most conservative signal
    if _first_last_match(a, b):
        return True

    return False


def is_sanctions_match(input_name: str, sanctions_name: str) -> bool:
    """
    Stricter matching for UN / RBI sanctions lists.
    Precision matters more here — a false positive blocks a legitimate customer.

    Strategy:
    - Primary: token_sort_ratio >= SANCTIONS_FULL_MATCH_THRESHOLD
    - Secondary: token_set_ratio >= SANCTIONS_SET_RATIO_THRESHOLD
      (catches subset matches like partial name entries in XML)
    - For 4+ word names also require meaningful token overlap >= 0.75
    """
    a = normalize_name(input_name)
    b = normalize_name(sanctions_name)

    sort_score = fuzz.token_sort_ratio(a, b)
    set_score  = fuzz.token_set_ratio(a, b)

    if sort_score >= SANCTIONS_FULL_MATCH_THRESHOLD:
        # Extra guard for long names: also check token overlap
        tokens_a = _meaningful_tokens(a)
        if len(tokens_a) >= 4:
            if _token_overlap_ratio(a, b) < 0.75:
                return False
        return True

    if set_score >= SANCTIONS_SET_RATIO_THRESHOLD:
        # For set-ratio hits on long names, demand stronger token overlap
        tokens_a = _meaningful_tokens(a)
        if len(tokens_a) >= 4:
            return _token_overlap_ratio(a, b) >= 0.75
        return True

    return False


def is_pep_match(input_name: str, candidate_name: str) -> bool:
    """
    Matching for Politically Exposed Persons (Myneta).
    Uses a high threshold since PEP flagging has regulatory consequences.
    """
    a = normalize_name(input_name)
    b = normalize_name(candidate_name)

    sort_score = fuzz.token_sort_ratio(a, b)

    if sort_score >= PEP_MATCH_THRESHOLD:
        # For long names, also require most tokens to match
        tokens_a = _meaningful_tokens(a)
        if len(tokens_a) >= 4:
            return _token_overlap_ratio(a, b) >= 0.80
        return True

    return False


def fuzzy_match_sanctions_list(name: str, sanctions_list: list[str]) -> list[tuple[str, int]]:
    """
    Screen a name against an entire sanctions list.
    Returns a list of (matched_name, score) tuples for all hits.
    """
    matches = []
    a = normalize_name(name)

    for entry in sanctions_list:
        b = normalize_name(entry)
        score = fuzz.token_sort_ratio(a, b)

        if is_sanctions_match(name, entry):
            matches.append((entry, score))

    return matches
