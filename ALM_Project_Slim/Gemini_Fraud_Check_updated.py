"""
Gemini_Fraud_Check.py
─────────────────────
Web-based Adverse Media & Fraud Risk Check powered by Google Gemini.
Generates a professional PDF report using ReportLab.
"""

# =========================================================
# Imports
# =========================================================
import os
import re
import json
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types
from reportlab.lib import pagesizes, colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle)


# =========================================================
# Configuration  ← Edit these values for your environment
# =========================================================
GEMINI_MODEL    = "gemini-2.5-flash"                    # Model to use
LOGO_PATH       = "PAI_logo_inline.png"                 # Abs path to logo PNG/JPG, or "" to skip
OUTPUT_DIR      = str(Path.home() / "Fraud_check_reports")  # Output folder (auto-created)
OUTPUT_FILENAME = "Fraud_Check_Report"                   # Base filename (customer name is appended)


# =========================================================
# 1. Clean & Parse Gemini JSON Safely
# =========================================================
def clean_and_parse_json(response_text: str) -> dict:
    """
    Strips markdown fences and extracts the first valid JSON object.
    Raises ValueError if no valid JSON is found or parsing fails.
    """
    cleaned = re.sub(r"```json|```", "", response_text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(
            f"No valid JSON found in model response.\n\nRaw response:\n{response_text}"
        )
    return json.loads(match.group(0))


# =========================================================
# 2. Gemini Fraud Check
# =========================================================
def run_gemini_fraud_check(
    customer_name: str,
    place: str,
    mobile: str,
    company: str,           # FIX 1: was misspelled as "comapny", causing NameError in the f-string
) -> dict:
    """
    Calls Gemini with Google Search grounding to perform adverse media
    and fraud risk analysis. Returns a parsed dict of results.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Set it with: export GEMINI_API_KEY=your_key"
        )

    client = genai.Client(api_key=api_key)

    # FIX 2: Corrected JSON template in prompt:
    #   - "UN Sanction Appearence": "Yes or "No"  →  missing closing quote after Yes + missing comma
    #   - Spelling: "Appearence" → "Appearance", "through" → "thorough"
    prompt = f"""
You are a financial crime risk analyst.

Perform a thorough adverse media and fraud risk web search using keywords such as:
FIR lodged, Tax Evasion, GST suo moto, Misappropriation of funds, Fraud, Scam,
Chit fund, Criminal, Anti money laundering, Civil Suit, Default, Phone risk
on sites like Crime Check, My Neta, eCourts, Indian Kanoon, and News sources.

Check if the Name or Identifier/Company_Name appears in prominent Indian news channels
such as ANI, Times of India, The Indian Express, Aaj Tak, and NDTV.

Scan social media platforms — Facebook, Instagram, LinkedIn, YouTube, and Naukri.com —
for any adverse media findings. Note any political exposure found on Instagram.

Also check if the name appears in the United Nations Sanctions List.

Subject details:
    Name:                    {customer_name}
    Location:                {place}
    Identifier/Company Name: {company}
    Mobile:                  {mobile}

Return ONLY valid JSON in this exact format (no markdown, no commentary):

{{
    "Fraud Mentions Found": <integer>,
    "Criminal Case Mentions": <integer>,
    "UN Sanction Appearance": "Yes" or "No",
    "Political Exposure": "Yes" or "No",
    "Final Risk Score": <integer 0-100>,
    "Risk Category": "Low" or "Medium" or "High",
    "Summary": "<Detailed professional explanation>"
}}

Scoring rules:
- Normalise Final Risk Score between 0 and 100.
- Assign Final Risk Score > 50 and Risk Category "High" when Fraud Mentions Found
  OR Criminal Case Mentions is greater than 1.
"""

    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[grounding_tool])

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    return clean_and_parse_json(response.text)


# =========================================================
# 3. Shared Table Style Helper
# =========================================================
def _make_table_style() -> TableStyle:
    """Returns a consistent TableStyle for both data tables in the report."""
    return TableStyle([
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#F2F2F2")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.HexColor("#222222")),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  10.5),
        ("ALIGN",         (0, 0), (-1, 0),  "LEFT"),
        ("LINEABOVE",     (0, 0), (-1, 0),  0.8, colors.HexColor("#E5E5E5")),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.8, colors.HexColor("#E5E5E5")),
        # Data rows
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 10.5),
        ("TEXTCOLOR",     (0, 1), (-1, -1), colors.HexColor("#222222")),
        ("INNERGRID",     (0, 1), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),
        # Box & padding
        ("BOX",           (0, 0), (-1, -1), 0.6,  colors.HexColor("#E5E5E5")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])


# =========================================================
# 4. PDF Generator
# =========================================================
def generate_pdf(data: dict, file_path: str, logo_path: str = "") -> None:
    """
    Generate a professional Web Fraud Check Report PDF.

    Parameters
    ----------
    data : dict
        {"inputs": {...}, "outputs": {...}}
    file_path : str
        Destination path for the PDF file.
    logo_path : str
        Optional path to a logo image. Omitted if empty or file not found.
    """
    # FIX 3: Ensure the output directory exists before writing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    LEFT_MARGIN  = 0.75 * inch
    RIGHT_MARGIN = 0.75 * inch
    PAGE_W       = pagesizes.A4[0]
    AVAIL_W      = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN   # ≈ 487 pts / 6.77 in
    COL1_W       = 2.2 * inch                            # "Field / Metric" column
    COL2_W       = AVAIL_W - COL1_W                      # "Value" column fills the rest

    doc = SimpleDocTemplate(
        file_path,
        pagesize=pagesizes.A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=1 * inch,
        bottomMargin=0.8 * inch,
    )

    styles = getSampleStyleSheet()

    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=8,
    )
    summary_style = ParagraphStyle(
        "Summary",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_JUSTIFY,
    )

    # --------------------------------------------------
    # Header / Footer  (drawn on every page via canvas)
    # --------------------------------------------------
    def draw_header_footer(canv: canvas.Canvas, _doc):
        width, height = pagesizes.A4
        header_y = height - 0.6 * inch
        left_x  = doc.leftMargin
        right_x = width - doc.rightMargin

        # Title
        canv.setFont("Helvetica-Bold", 16)
        canv.setFillColor(colors.HexColor("#0F172A"))
        canv.drawString(left_x, header_y, "Web Fraud Check Report by ✦GeminiAI")

        # Timestamp
        canv.setFont("Helvetica", 9.5)
        canv.setFillColor(colors.HexColor("#475569"))
        gen_time = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
        canv.drawString(left_x, header_y - 14, f"Report generated on: {gen_time}")

        # Logo (right-aligned, graceful fallback)
        # FIX 4: Removed dead `img = Image(logo_path)` line; ImageReader import moved to top
        if logo_path and os.path.isfile(logo_path):
            try:
                max_w, max_h = 120, 36
                ir = ImageReader(logo_path)
                iw, ih = ir.getSize()
                scale = min(max_w / iw, max_h / ih)
                w, h = iw * scale, ih * scale
                canv.drawImage(
                    logo_path,
                    right_x - w,
                    header_y - (h - 6),
                    width=w,
                    height=h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                canv.setFont("Helvetica-Oblique", 9)
                canv.setFillColor(colors.HexColor("#64748B"))
                canv.drawRightString(right_x, header_y, "Company Logo")

        # Red divider
        canv.setStrokeColor(colors.HexColor("#DF0024"))
        canv.setLineWidth(0.8)
        canv.line(left_x, header_y - 22, right_x, header_y - 22)

        # Page number
        canv.setFont("Helvetica", 9)
        canv.setFillColor(colors.HexColor("#475569"))
        canv.drawRightString(right_x, 0.5 * inch, f"Page {canv.getPageNumber()}")

    # --------------------------------------------------
    # Flowables
    # --------------------------------------------------
    elements = [Spacer(1, 0.1 * inch)]

    # --- Customer Input Table ---
    elements.append(Paragraph("Customer Input Details", h2_style))
    elements.append(Spacer(1, 0.06 * inch))

    inputs = data.get("inputs") or {}
    input_rows = [["Field", "Value"]] + [
        [str(k), "" if v is None else str(v)] for k, v in inputs.items()
    ]
    inputs_table = Table(input_rows, colWidths=[COL1_W, COL2_W])
    inputs_table.setStyle(_make_table_style())
    elements.append(inputs_table)
    elements.append(Spacer(1, 0.25 * inch))

    # --- Fraud Analysis Results Table ---
    elements.append(Paragraph("Fraud Analysis Results", h2_style))
    elements.append(Spacer(1, 0.06 * inch))

    outputs = data.get("outputs") or {}

    # Colour-code the Risk Category cell
    RISK_COLORS = {
        "low":    colors.HexColor("#166534"),   # dark green
        "medium": colors.HexColor("#92400E"),   # dark amber
        "high":   colors.HexColor("#991B1B"),   # dark red
    }
    RISK_BG = {
        "low":    colors.HexColor("#DCFCE7"),
        "medium": colors.HexColor("#FEF3C7"),
        "high":   colors.HexColor("#FEE2E2"),
    }

    result_rows = [["Metric", "Value"]]
    risk_row_index = None
    for k, v in outputs.items():
        if k == "Summary":
            continue
        if k == "Risk Category":
            risk_row_index = len(result_rows)
        result_rows.append([str(k), "" if v is None else str(v)])

    results_table = Table(result_rows, colWidths=[COL1_W, COL2_W])
    ts = _make_table_style()

    # Apply conditional colour to Risk Category row
    if risk_row_index is not None:
        risk_val = (outputs.get("Risk Category") or "").strip().lower()
        bg  = RISK_BG.get(risk_val,    colors.HexColor("#F2F2F2"))
        txt = RISK_COLORS.get(risk_val, colors.HexColor("#222222"))
        ts.add("BACKGROUND", (0, risk_row_index), (-1, risk_row_index), bg)
        ts.add("TEXTCOLOR",  (0, risk_row_index), (-1, risk_row_index), txt)
        ts.add("FONTNAME",   (0, risk_row_index), (-1, risk_row_index), "Helvetica-Bold")

    results_table.setStyle(ts)
    elements.append(results_table)
    elements.append(Spacer(1, 0.25 * inch))

    # --- Analyst Summary ---
    elements.append(Paragraph("Web Search Summary", h2_style))
    elements.append(Spacer(1, 0.06 * inch))

    summary_text = (outputs.get("Summary") or "—").replace("₹", "Rs.")
    elements.append(Paragraph(summary_text, summary_style))

    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)


# =========================================================
# 5. Main Execution
# =========================================================
def main() -> None:
    print("=" * 60)
    print("  Web Fraud Check  ✦  Powered by Gemini AI")
    print("=" * 60)

    customer_name = input("\nCustomer Name                        : ").strip()
    place         = input("Place of Residence / Business        : ").strip()
    company       = input("Identifier or Business Name          : ").strip()
    mobile_number = input("Mobile Number                        : ").strip()

    if not customer_name:
        raise ValueError("Customer name cannot be empty.")

    customer_input = {
        "Customer Name":         customer_name,
        "Place of Residence":    place,
        "Mobile Number":         mobile_number,
        "Business / Identifier": company,
    }

    print("\n Running Gemini web search — this may take 15-30 seconds …\n")

    gemini_output = run_gemini_fraud_check(customer_name, place, mobile_number, company)

    final_data = {"inputs": customer_input, "outputs": gemini_output}

    # Build output path: <OUTPUT_DIR>/<OUTPUT_FILENAME>_<customer_name>.pdf
    # FIX 3 (continued): Path built from config; os.makedirs inside generate_pdf handles creation
    customer_slug = re.sub(r"[^\w]", "_", customer_name).lower()
    out_path = os.path.join(OUTPUT_DIR, f"{OUTPUT_FILENAME}_{customer_slug}.pdf")

    generate_pdf(final_data, out_path, logo_path=LOGO_PATH)

    print(f" Report generated: {out_path}")

    # Also pretty-print the JSON result to the terminal for a quick view
    print("\n--- Quick Result ---")
    for k, v in gemini_output.items():
        if k != "Summary":
            print(f"  {k:<28}: {v}")
    print(f"\n  Summary:\n  {gemini_output.get('Summary', '—')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
    except Exception as exc:
        print(f"\n ERROR: {exc}")