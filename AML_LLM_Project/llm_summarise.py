import os
import json
import google.generativeai as genai


def summarize_with_llm(evidence, score, category):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "LLM summary unavailable: GEMINI_API_KEY not set."

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        prompt = f"""
You are a compliance risk analyst.

Below is adverse media and legal evidence collected for a subject.

EVIDENCE:
{json.dumps(evidence, indent=2)}

RISK SCORE: {score}
RISK CATEGORY: {category}

Provide a professional compliance summary including:
- Key risk findings
- Nature of allegations (if any)
- Sanctions exposure (if applicable)
- Overall risk interpretation
- Recommendation for enhanced due diligence (if required)

Keep tone formal and suitable for a regulatory compliance report.
"""

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        return f"LLM summarization failed: {str(e)}"