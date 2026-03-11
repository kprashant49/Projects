"""
main.py — Entry point for the AML Screening System.

Usage (interactive):
    python main.py

Usage (CLI arguments):
    python main.py --name "Raj Kumar Sharma" --place "Mumbai" --mobile "9876543210" --pan "ABCDE1234F"
"""

import argparse
import json

from evidence_aggregator import collect_evidence
from sanctions import load_un_sanctions
from name_matcher import fuzzy_match_sanctions_list
from risk_scoring import calculate_risk
from llm_summarise import summarize_with_llm
from report_generator import generate_pdf_report
from config import DATA_DIR


def run_aml_check(
    name:   str,
    place:  str,
    mobile: str | None = None,
    pan:    str | None = None,
) -> dict:
    """
    Run a full AML screening for one subject.
    Returns a result dict containing scores, evidence, and narrative summary.
    """
    print(f"\n[AML] Starting screening for: {name} ({place})")

    print("[AML] Collecting evidence...")
    evidence = collect_evidence(name, place, mobile, pan)
    print(f"[AML] Evidence items collected: {len(evidence)}")

    print("[AML] Loading UN sanctions list...")
    sanctions_names = load_un_sanctions(DATA_DIR / "un_sanctions.xml")

    print("[AML] Performing sanctions screening...")
    sanctions_matches = fuzzy_match_sanctions_list(name, sanctions_names)
    sanctions_flag    = len(sanctions_matches) > 0

    print("[AML] Calculating risk score...")
    score, category, breakdown = calculate_risk(evidence, sanctions_flag, mobile, pan)
    print(f"[AML] Risk score: {score} ({category})")

    print("[AML] Generating compliance summary...")
    summary = summarize_with_llm(evidence, score, category, breakdown)

    return {
        "name":              name,
        "place":             place,
        "risk_score":        score,
        "risk_category":     category,
        "score_breakdown":   breakdown,
        "sanctions_flag":    sanctions_flag,
        "sanctions_matches": sanctions_matches,
        "evidence_count":    len(evidence),
        "evidence":          evidence,
        "summary":           summary,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AML Screening System")
    parser.add_argument("--name",   help="Full name of the subject")
    parser.add_argument("--place",  help="Place of residence")
    parser.add_argument("--mobile", help="Mobile number (optional)", default=None)
    parser.add_argument("--pan",    help="PAN number (optional)",    default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    # Fall back to interactive input if arguments are not provided
    name   = args.name   or input("Name of Customer:    ").strip()
    place  = args.place  or input("Place of Residence:  ").strip()
    mobile = args.mobile or input("Mobile Number (leave blank to skip): ").strip() or None
    pan    = args.pan    or input("PAN Number (leave blank to skip):    ").strip() or None

    report   = run_aml_check(name, place, mobile, pan)
    pdf_path = generate_pdf_report(report)

    print("\n" + "=" * 60)
    print(json.dumps(report, indent=2))
    print("=" * 60)
    print(f"\n[AML] PDF report saved to: {pdf_path}")
