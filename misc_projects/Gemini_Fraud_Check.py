import os
import re
import json
from datetime import datetime
from google import genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch


# =========================================================
# 1️. Clean & Parse Gemini JSON Safely
# =========================================================
def clean_and_parse_json(response_text: str) -> dict:
    """
    Removes markdown fences and extracts first valid JSON object.
    Raises error if JSON is invalid.
    """

    # Remove markdown code blocks if present
    cleaned = re.sub(r"```json|```", "", response_text).strip()

    # Extract first JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not match:
        raise ValueError("No valid JSON found in model response")

    json_text = match.group(0)

    return json.loads(json_text)


# =========================================================
# 2️. Gemini Fraud Check
# =========================================================
def run_gemini_fraud_check(customer_name: str, place: str, mobile: str) -> dict:

    client = genai.Client(api_key="AIzaSyDD-C5wF1xkkl9z_UzqAM8YynIq7IKynYs")

    # if not api_key:
    #     raise ValueError("GEMINI_API_KEY environment variable not set")

    # client = genai.Client(api_key=api_key)

    prompt = f"""
            You are a financial crime risk analyst.

            Perform adverse media and fraud risk analysis for:

            Name: {customer_name}
            Location: {place}
            Mobile: {mobile}

            Return ONLY valid JSON in this exact format:

            {{
                "Fraud Mentions Found": number,
                "Criminal Case Mentions": number,
                "Political Exposure": "Yes" or "No",
                "Final Risk Score": number,
                "Risk Category": "Low" or "Medium" or "High",
                "Summary": "Short professional explanation"
            }}

            Do NOT wrap in markdown.
            Do NOT add commentary.
            """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    parsed = clean_and_parse_json(response.text)

    return parsed


# =========================================================
# 3️. Reusable PDF Generator (No Tables)
# =========================================================
def generate_pdf(data: dict, file_path: str):

    doc = SimpleDocTemplate(file_path, pagesize=pagesizes.A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("Web Fraud Check Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Timestamp
    elements.append(
        Paragraph(
            f"Report Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )
    )
    elements.append(Spacer(1, 0.4 * inch))

    # =========================
    # Customer Inputs
    # =========================
    elements.append(Paragraph("Customer Input Details", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    for key, value in data["inputs"].items():
        elements.append(
            Paragraph(f"<b>{key}:</b> {value}", styles["Normal"])
        )
        elements.append(Spacer(1, 0.15 * inch))

    elements.append(Spacer(1, 0.4 * inch))

    # =========================
    # Fraud Results
    # =========================
    elements.append(Paragraph("Fraud Analysis Results", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    for key, value in data["outputs"].items():
        if key != "Summary":
            elements.append(
                Paragraph(f"<b>{key}:</b> {value}", styles["Normal"])
            )
            elements.append(Spacer(1, 0.15 * inch))

    elements.append(Spacer(1, 0.4 * inch))

    # =========================
    # Analyst Summary
    # =========================
    elements.append(Paragraph("Analyst Summary", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(
        Paragraph(data["outputs"]["Summary"], styles["Normal"])
    )

    doc.build(elements)


# =========================
# 4️. Main Execution
# =========================

if __name__ == "__main__":

    print("*** Welcome to Web Fraud Check based on GeminiAI ***")

    customer_name = input("Customer Name: ")
    place = input("Place of Residence: ")
    mobile_number = input("Mobile Number: ")

    customer_input = {
        "Customer Name": customer_name,
        "Place of Residence": place,
        "Mobile Number": mobile_number
    }

    try:
        gemini_output = run_gemini_fraud_check(
            customer_name,
            place,
            mobile_number
        )

        final_data = {
            "inputs": customer_input,
            "outputs": gemini_output
        }

        file_path = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Fraud_Check_Reports\Fraud_Check_Report.pdf"
        customer_name_clean = customer_name.replace(" ", "_").lower()
        new_file_path = file_path.replace(".pdf", f"_{customer_name_clean}.pdf")
        generate_pdf(final_data, new_file_path)

        print(f"\nReport generated successfully: {new_file_path}")

    except Exception as e:
        print("\nERROR:", str(e))