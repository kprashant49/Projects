import json
from evidence_aggregator import collect_evidence
from sanctions import load_un_sanctions
from rbi_fuzzy_match import fuzzy_match_name
from risk_scoring import calculate_risk
from llm_summarise import summarize_with_llm


def run_alm_check(name, place):

    print("Collecting evidence...")
    evidence = collect_evidence(name, place)

    print("Loading sanctions list...")
    sanctions_names = load_un_sanctions("data/un_sanctions.xml")

    print("Performing sanctions screening...")
    sanctions_matches = fuzzy_match_name(name, sanctions_names)

    sanctions_flag = len(sanctions_matches) > 0

    print("Calculating risk score...")
    score, category, breakdown = calculate_risk(evidence, sanctions_flag)

    print("Generating compliance summary...")
    summary = summarize_with_llm(evidence, score, category, breakdown)

    result = {
        "name": name,
        "place": place,
        "risk_score": score,
        "risk_category": category,
        "score_breakdown": breakdown,
        "sanctions_flag": sanctions_flag,
        "sanctions_matches": sanctions_matches,
        "evidence_count": len(evidence),
        "evidence": evidence,
        "summary": summary
    }

    return result


if __name__ == "__main__":

    name = "Vijay Mallya"
    place = "India"

    report = run_alm_check(name, place)

    print(json.dumps(report, indent=2))