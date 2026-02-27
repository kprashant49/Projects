import os
import json
from openai import AzureOpenAI


def summarize_with_llm(evidence, score, category, breakdown):

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not api_key or not deployment:
        return "Azure OpenAI configuration missing."

    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-01",
            azure_endpoint=endpoint
        )

        prompt = f"""
        You are a compliance risk analyst.

        EVIDENCE:
        {json.dumps(evidence[:10], indent=2)}

        SCORE BREAKDOWN:
        Fraud Hits: {breakdown['fraud_hits']}
        Fraud Score: {breakdown['fraud_score']}
        Sanctions Match: {breakdown['sanctions_match']}
        Sanctions Score: {breakdown['sanctions_score']}
        PEP Hits: {breakdown['pep_hits']}
        PEP Score: {breakdown['pep_score']}
        Total Score: {breakdown['total_score']}
        Risk Category: {category}

        Provide a professional compliance summary suitable for regulatory reporting.
        """

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a professional AML compliance analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Azure LLM summarization failed: {str(e)}"