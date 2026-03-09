import os
import re
import json
from google import genai
from google.genai import types
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from google.genai import Client
from google.genai.types import GenerateContentConfig, GoogleSearch
from reportlab.lib import pagesizes, colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os


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
def run_gemini_fraud_check(customer_name: str, place: str, mobile: str, comapny: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)


    prompt = f"""
            You are a financial crime risk analyst.

            Perform adverse media and fraud risk websearch which include keywords like: 
            FIR lodged, Tax Evasion, GST suo moto, Misappropriation of funds, Fraud, Scam, Chit fund, Criminal, Anti money laundering, Civil Suit,
            Default, Phone risk on various sites like Crime check, My Neta, eCourts, News and Indian Kanoon.
            Check if the Name, Identifier/Company_Name appears in any prominent News Channels like ANI, Times of India, The Indian Express, Aaj Tak, and NDTV etc.
            Additionally, also scan Social Media sites Facebook, Instagram, LinkedIn, Youtube and Naukri.com for any Adverse media findings and Political link in Instagram
            Also, check if the name appears in United Nations Sanction List.
            for:

            Name: {customer_name}
            Location: {place}
            Identifier/Company_Name: {company}
            Mobile: {mobile}

            Do a through analysis of the web search.
            Return ONLY valid JSON in this exact format:

            {{
                "Fraud Mentions Found": number,
                "Criminal Case Mentions": number,
                "UN Sanction Appearence": "Yes or "No"
                "Political Exposure": "Yes" or "No",
                "Final Risk Score": number,
                "Risk Category": "Low" or "Medium" or "High",
                "Summary": "Detailed professional explanation"
            }}

            Normalise the score between 0 to 100.
            Give higher (>50) "Final Risk Score" and high "Risk Category" whenever "Fraud Mentions Found" and "Criminal Case Mentions" is more than 1.

            Do NOT wrap in markdown.
            Do NOT add commentary.
            """

    # response = client.models.generate_content(
    #     model="gemini-3-flash-preview",
    #     contents=prompt,
    #     tools=[GoogleSearch]
    # )

    grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    parsed = clean_and_parse_json(response.text)

    return parsed


# =========================================================
# 3️. Reusable PDF Generator (No Tables)
# =========================================================

def generate_pdf(data: dict, file_path: str,
                 logo_path: str = r"D:\Projects\AML_LLM_Project\PAI_logo_inline.png"):
    """
    Generate a professional 'Web Fraud Check Report' PDF with:
      - Top header (title/subtitle on left, logo on right)
      - Inputs and outputs shown as styled tables
      - Analyst summary with better typography
      - Footer with page numbers

    Parameters
    ----------
    data : dict
        {
          "inputs": { ... },
          "outputs": { "Summary": "...", ... }
        }
    file_path : str
        Output PDF path.
    logo_path : str, optional
        Path to the company logo image (PNG/JPG). If None or invalid, header is text-only.
    """

    # -----------------------------
    # Document Setup & Styles
    # -----------------------------
    doc = SimpleDocTemplate(
        file_path,
        pagesize=pagesizes.A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=1 * inch,  # Leave extra room for the header
        bottomMargin=0.8 * inch
    )

    styles = getSampleStyleSheet()

    # Base styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),  # slate-900
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#475569")  # slate-600
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=8
    )
    normal_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F172A")
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#475569")
    )

    # -----------------------------
    # Header / Footer Draw Functions
    # -----------------------------
    def draw_header_footer(canv: canvas.Canvas, doc_obj):
        # Page size
        width, height = pagesizes.A4

        # Header content box
        header_y = height - 0.6 * inch
        left_x = doc.leftMargin
        right_x = width - doc.rightMargin

        # Left: Title and subtitle
        canv.setFont("Helvetica-Bold", 16)
        canv.setFillColor(colors.HexColor("#0F172A"))
        canv.drawString(left_x, header_y, "Web Fraud Check Report by ✦GeminiAI")

        canv.setFont("Helvetica", 9.5)
        canv.setFillColor(colors.HexColor("#475569"))
        gen_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        canv.drawString(left_x, header_y - 14, f"Report generated on: {gen_time}")

        # Right: Logo (if provided)
        if logo_path and os.path.isfile(logo_path):
            try:
                # Fit logo into a box (max 120x36 pts) while preserving aspect ratio
                max_w, max_h = 120, 36
                img = Image(logo_path)
                # Temporarily load to get intrinsic size (workaround: drawImage handles scaling directly)
                # We'll measure with a conservative approach: assume typical logo aspect ratio
                # and compute scale based on one constraint.
                from reportlab.lib.utils import ImageReader
                ir = ImageReader(logo_path)
                iw, ih = ir.getSize()
                scale = min(max_w / iw, max_h / ih)
                w, h = iw * scale, ih * scale
                canv.drawImage(
                    logo_path,
                    right_x - w,  # align to right margin
                    header_y - (h - 6),  # minor vertical alignment tweak
                    width=w,
                    height=h,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception:
                # Fallback to text if image fails
                canv.setFont("Helvetica-Oblique", 9)
                canv.setFillColor(colors.HexColor("#64748B"))
                canv.drawRightString(right_x, header_y, "Company Logo")

        # Divider line under header
        canv.setStrokeColor(colors.HexColor("#DF0024"))
        canv.setLineWidth(0.8)
        canv.line(doc.leftMargin, header_y - 22, right_x, header_y - 22)

        # Footer: page number
        canv.setFont("Helvetica", 9)
        canv.setFillColor(colors.HexColor("#475569"))
        page_str = f"Page {canv.getPageNumber()}"
        canv.drawRightString(right_x, 0.5 * inch, page_str)

    # -----------------------------
    # Flowables
    # -----------------------------
    elements = []

    # Optional intro (kept minimal as header now contains title/time)
    elements.append(Spacer(1, 0.1 * inch))

    # ---------- Customer Inputs (Table) ----------
    elements.append(Paragraph("Customer Input Details", h2_style))
    elements.append(Spacer(1, 0.06 * inch))

    inputs = data.get("inputs", {}) or {}
    input_rows = [["Field", "Value"]]
    for k, v in inputs.items():
        input_rows.append([str(k), "" if v is None else str(v)])

    inputs_table = Table(
        input_rows,
        colWidths=[2.2 * inch, None]
    )
    inputs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),  # header
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#222222")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10.5),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#222222")),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.HexColor("#E5E5E5")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#E5E5E5")),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E5E5E5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(inputs_table)
    elements.append(Spacer(1, 0.25 * inch))

    # ---------- Fraud Analysis Results (Table) ----------
    elements.append(Paragraph("Fraud Analysis Results", h2_style))
    elements.append(Spacer(1, 0.06 * inch))

    outputs = data.get("outputs", {}) or {}
    result_rows = [["Metric", "Value"]]
    for k, v in outputs.items():
        if k != "Summary":
            result_rows.append([str(k), "" if v is None else str(v)])

    results_table = Table(
        result_rows,
        colWidths=[2.2 * inch, None]
    )
    results_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),  # header
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#222222")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#222222")),
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.HexColor("#E5E5E5")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#E5E5E5")),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#E5E5E5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(results_table)
    elements.append(Spacer(1, 0.25 * inch))

    # ---------- Analyst Summary ----------
    elements.append(Paragraph("Websearch Summary", h2_style))
    elements.append(Spacer(1, 0.06 * inch))

    summary_style = ParagraphStyle(
        "Summary",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_JUSTIFY
    )

    summary_text = outputs.get("Summary", "—")
    summary_text = summary_text.replace("₹", "Rs.")
    elements.append(Paragraph(summary_text, summary_style))

    # Build with header/footer on every page
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)


# =========================
# 4️. Main Execution
# =========================

if __name__ == "__main__":

    print(">>> Welcome to Web Fraud Check powered by ✦GeminiAI! <<<")

    customer_name = input("Customer Name: ")
    place = input("Place of Residence/Business: ")
    company = input("Please input a prominent identifier or Business_Name: ")
    mobile_number = input("Mobile Number: ")

    customer_input = {
        "Customer Name": customer_name,
        "Place of Residence": place,
        "Mobile Number": mobile_number,
        "Business_Name/Identifier": company
    }

    try:
        gemini_output = run_gemini_fraud_check(
            customer_name,
            place,
            mobile_number,
            company
        )

        final_data = {
            "inputs": customer_input,
            "outputs": gemini_output
        }

        file_path = r"C:\Users\kpras\Desktop\Test_data\Fraud_check_reports\Fraud_Check_Report.pdf"
        customer_name_clean = customer_name.replace(" ", "_").lower()
        new_file_path = file_path.replace(".pdf", f"_{customer_name_clean}.pdf")
        generate_pdf(final_data, new_file_path)

        print(f"\nReport generated successfully: {new_file_path}")

    except Exception as e:
        print("\nERROR:", str(e))
