"""
llm_summarise.py — Generate a professional compliance summary via Azure OpenAI.
"""

import json
import time
from openai import AzureOpenAI

from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT,
    MAX_EVIDENCE_FOR_LLM,
)

_MAX_RETRIES = 2


def summarize_with_llm(
    evidence:  list[dict],
    score:     int,
    category:  str,
    breakdown: dict,
) -> str:
    """
    Send evidence and score breakdown to Azure OpenAI and return a
    professional AML compliance narrative.

    Retries once on transient errors before giving up.
    """
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT]):
        return "Azure OpenAI configuration is incomplete — summary unavailable."

    client = AzureOpenAI(
        api_key       = AZURE_OPENAI_API_KEY,
        api_version   = "2024-02-01",
        azure_endpoint = AZURE_OPENAI_ENDPOINT,
    )

    prompt = f"""
You are a compliance risk analyst preparing a regulatory report.

EVIDENCE (top {MAX_EVIDENCE_FOR_LLM} items):
{json.dumps(evidence[:MAX_EVIDENCE_FOR_LLM], indent=2)}

SCORE BREAKDOWN:
  Fraud Hits:       {breakdown['fraud_hits']}
  Fraud Score:      {breakdown['fraud_score']}
  Sanctions Match:  {breakdown['sanctions_match']}
  Sanctions Score:  {breakdown['sanctions_score']}
  PEP Hits:         {breakdown['pep_hits']}
  PEP Score:        {breakdown['pep_score']}
  Mobile Hits:      {breakdown.get('mobile_hits', 0)}
  Mobile Score:     {breakdown.get('mobile_score', 0)}
  PAN Hits:         {breakdown.get('pan_hits', 0)}
  PAN Score:        {breakdown.get('pan_score', 0)}
  Total Score:      {breakdown['total_score']}
  Risk Category:    {category}

Write a concise, professional compliance summary (200–300 words) suitable for
inclusion in a regulatory filing. Cite specific evidence where relevant.
Do not invent facts not present in the evidence list.
"""

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model       = AZURE_OPENAI_DEPLOYMENT,
                messages    = [
                    {"role": "system",  "content": "You are a professional AML compliance analyst."},
                    {"role": "user",    "content": prompt},
                ],
                temperature = 0.2,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[LLM] Azure OpenAI attempt {attempt} failed: {e}")
            if attempt < _MAX_RETRIES:
                time.sleep(2)

    return "LLM summarization failed after retries — please review the evidence manually."
