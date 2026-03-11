"""
config.py — Central configuration for the AML Screening System.

All API keys are loaded from environment variables (via a .env file).
Feature flags, scoring weights, thresholds, and paths are all defined here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Directory Layout
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).parent
DATA_DIR   = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# API Keys  (set these in your .env file — never commit real values)
# ---------------------------------------------------------------------------
SERPAPI_KEY             = os.getenv("SERPAPI_KEY", "")
GNEWS_KEY               = os.getenv("GNEWS_KEY", "")
NEWS_API_KEY            = os.getenv("NEWS_API_KEY", "")
AZURE_OPENAI_ENDPOINT   = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY    = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

# ---------------------------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------------------------
# Set to True only if Chrome + ChromeDriver are available in your environment.
USE_SELENIUM_INDIAN_KANOON = False
USE_SELENIUM_MYNETA        = False

# ---------------------------------------------------------------------------
# Report Assets
# ---------------------------------------------------------------------------
LOGO_PATH = ASSETS_DIR / r"D:\Projects\ALM_Project_Refactored\PAI_logo_inline.png"

# ---------------------------------------------------------------------------
# Risk Scoring Weights
# ---------------------------------------------------------------------------
FRAUD_SCORE_PER_HIT    = 15   # points added per article with a fraud keyword
FRAUD_SCORE_MAX        = 45   # cap on total fraud score
SANCTIONS_SCORE        = 70   # flat score when a sanctions match is found
PEP_SCORE              = 25   # flat score when a PEP (Myneta) hit is found
MOBILE_SCORE           = 15   # flat score when mobile number appears in evidence
PAN_SCORE              = 20   # flat score when PAN number appears in evidence

RISK_HIGH_THRESHOLD    = 50   # score >= this → High risk
RISK_MEDIUM_THRESHOLD  = 35   # score >= this → Medium risk (else Low)

# ---------------------------------------------------------------------------
# Name-Matching Thresholds  (all values are 0–100 RapidFuzz scores)
# ---------------------------------------------------------------------------
# Used in evidence title filtering (recall-oriented, slightly more lenient)
EVIDENCE_FILTER_TOKEN_SORT_THRESHOLD  = 75
EVIDENCE_FILTER_PARTIAL_RATIO_THRESHOLD = 80
EVIDENCE_FILTER_TOKEN_OVERLAP_RATIO   = 0.70  # fraction of meaningful tokens that must match

# Used for sanctions list screening (precision-oriented, strict)
SANCTIONS_FULL_MATCH_THRESHOLD        = 85
SANCTIONS_SET_RATIO_THRESHOLD         = 88

# Used for PEP / Myneta screening
PEP_MATCH_THRESHOLD                   = 90

# Minimum token length to be treated as "meaningful" (filters out initials / stop-words)
MIN_MEANINGFUL_TOKEN_LENGTH           = 3

# ---------------------------------------------------------------------------
# Evidence Collection
# ---------------------------------------------------------------------------
RISK_KEYWORDS = [
    "fraud", "scam", "criminal", "default", "launder", "embezzle", "BIFR",
    "arrest", "convict", "terror", "corrupt", "investigate", "regulator",
    "penal", "fine", "police", "charge", "enforce", "blacklist", "discipline",
    "court", "litigate", "politic", "alleged", "ponzi", "insolvent",
    "bankrupt", "legal action", "shell company", "indict", "tax evasion",
    "bribe", "prosecute", "watch list", "kickback", "sanction", "civil suit",
    "misappropriate", "insider trading", "market manipulate", "adverse media",
    "debar", "suspend", "wilful", "absconding", "fugitive", "offend", "forge",
    "false statement", "misrepresent", "money laundering",
]

MAX_EVIDENCE_FOR_LLM    = 10   # number of evidence items sent to Azure OpenAI
MAX_EVIDENCE_IN_REPORT  = 20   # number of evidence items printed in PDF
SEARCH_RESULTS_PER_QUERY = 5   # organic results fetched from SerpAPI per query
