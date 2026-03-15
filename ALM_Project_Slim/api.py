"""
api.py
──────
Self-contained Fraud Check API powered by Gemini AI.
All logic is in this single file — no sibling module imports needed.

Run:
    uvicorn api:app --reload --port 8000

Environment variable required:
    GEMINI_API_KEY=your_key
"""

# =========================================================
# Imports
# =========================================================
import os
import re
import json
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from reportlab.lib import pagesizes, colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)


# =========================================================
# Configuration  ← Edit these values for your environment
# =========================================================
GEMINI_MODEL    = "gemini-2.5-flash"
LOGO_PATH       = r"D:\Projects\AML_Project\PAI_logo_inline.png"   # or "" to skip
OUTPUT_DIR      = str(Path.home() / "Fraud_check_reports")
OUTPUT_FILENAME = "Fraud_Check_Report"


# =========================================================
# 1. Clean & Parse Gemini JSON Safely
# =========================================================
def clean_and_parse_json(response_text: str) -> dict:
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
    company: str,
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Set it with: set GEMINI_API_KEY=your_key"
        )

    client = genai.Client(api_key=api_key)

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
    return TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#F2F2F2")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.HexColor("#222222")),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0),  10.5),
        ("ALIGN",          (0, 0), (-1, 0),  "LEFT"),
        ("LINEABOVE",      (0, 0), (-1, 0),  0.8, colors.HexColor("#E5E5E5")),
        ("LINEBELOW",      (0, 0), (-1, 0),  0.8, colors.HexColor("#E5E5E5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 1), (-1, -1), 10.5),
        ("TEXTCOLOR",      (0, 1), (-1, -1), colors.HexColor("#222222")),
        ("INNERGRID",      (0, 1), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),
        ("BOX",            (0, 0), (-1, -1), 0.6,  colors.HexColor("#E5E5E5")),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
    ])


# =========================================================
# 4. PDF Generator
# =========================================================
def generate_pdf(data: dict, file_path: str, logo_path: str = "") -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    LEFT_MARGIN  = 0.75 * inch
    RIGHT_MARGIN = 0.75 * inch
    PAGE_W       = pagesizes.A4[0]
    AVAIL_W      = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    COL1_W       = 2.2 * inch
    COL2_W       = AVAIL_W - COL1_W

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

    def draw_header_footer(canv: canvas.Canvas, _doc):
        width, height = pagesizes.A4
        header_y = height - 0.6 * inch
        left_x   = doc.leftMargin
        right_x  = width - doc.rightMargin

        canv.setFont("Helvetica-Bold", 16)
        canv.setFillColor(colors.HexColor("#0F172A"))
        canv.drawString(left_x, header_y, "Web Fraud Check Report  ✦ Powered by Gemini AI")

        canv.setFont("Helvetica", 9.5)
        canv.setFillColor(colors.HexColor("#475569"))
        gen_time = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
        canv.drawString(left_x, header_y - 14, f"Report generated on: {gen_time}")

        if logo_path and os.path.isfile(logo_path):
            try:
                max_w, max_h = 120, 36
                ir = ImageReader(logo_path)
                iw, ih = ir.getSize()
                scale = min(max_w / iw, max_h / ih)
                w, h = iw * scale, ih * scale
                canv.drawImage(
                    logo_path, right_x - w, header_y - (h - 6),
                    width=w, height=h, preserveAspectRatio=True, mask="auto",
                )
            except Exception:
                canv.setFont("Helvetica-Oblique", 9)
                canv.setFillColor(colors.HexColor("#64748B"))
                canv.drawRightString(right_x, header_y, "Company Logo")

        canv.setStrokeColor(colors.HexColor("#DF0024"))
        canv.setLineWidth(0.8)
        canv.line(left_x, header_y - 22, right_x, header_y - 22)

        canv.setFont("Helvetica", 9)
        canv.setFillColor(colors.HexColor("#475569"))
        canv.drawRightString(right_x, 0.5 * inch, f"Page {canv.getPageNumber()}")

    elements = [Spacer(1, 0.1 * inch)]

    # Customer Input Table
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

    # Fraud Analysis Results Table
    elements.append(Paragraph("Fraud Analysis Results", h2_style))
    elements.append(Spacer(1, 0.06 * inch))
    outputs = data.get("outputs") or {}

    RISK_COLORS = {
        "low":    colors.HexColor("#166534"),
        "medium": colors.HexColor("#92400E"),
        "high":   colors.HexColor("#991B1B"),
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
    if risk_row_index is not None:
        risk_val = (outputs.get("Risk Category") or "").strip().lower()
        ts.add("BACKGROUND", (0, risk_row_index), (-1, risk_row_index), RISK_BG.get(risk_val,    colors.HexColor("#F2F2F2")))
        ts.add("TEXTCOLOR",  (0, risk_row_index), (-1, risk_row_index), RISK_COLORS.get(risk_val, colors.HexColor("#222222")))
        ts.add("FONTNAME",   (0, risk_row_index), (-1, risk_row_index), "Helvetica-Bold")
    results_table.setStyle(ts)
    elements.append(results_table)
    elements.append(Spacer(1, 0.25 * inch))

    # Summary
    elements.append(Paragraph("Web Search Summary", h2_style))
    elements.append(Spacer(1, 0.06 * inch))
    summary_text = (outputs.get("Summary") or "—").replace("₹", "Rs.")
    elements.append(Paragraph(summary_text, summary_style))

    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)


# =========================================================
# 5. FastAPI App
# =========================================================
app = FastAPI(
    title="Fraud Check API",
    description="Adverse media & fraud risk screening powered by Gemini AI",
    version="1.0.0",
)


class FraudCheckRequest(BaseModel):
    customer_name: str = Field(..., example="Rajesh Kumar")
    place:         str = Field(..., example="Mumbai")
    company:       str = Field("",  example="Kumar Enterprises")
    mobile:        str = Field("",  example="9876543210")


@app.post("/check", summary="Run fraud check — returns JSON")
def check_json(req: FraudCheckRequest):
    if not req.customer_name.strip():
        raise HTTPException(status_code=422, detail="customer_name cannot be empty.")
    try:
        result = run_gemini_fraud_check(
            req.customer_name, req.place, req.mobile, req.company
        )
        return {"inputs": req.model_dump(), "outputs": result}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check/report", summary="Run fraud check — returns PDF")
def check_pdf(req: FraudCheckRequest):
    if not req.customer_name.strip():
        raise HTTPException(status_code=422, detail="customer_name cannot be empty.")
    try:
        result = run_gemini_fraud_check(
            req.customer_name, req.place, req.mobile, req.company
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    slug = re.sub(r"[^\w]", "_", req.customer_name).lower()
    tmp  = tempfile.NamedTemporaryFile(
        suffix=f"_{slug}.pdf", delete=False, dir=tempfile.gettempdir()
    )
    tmp.close()

    generate_pdf({"inputs": req.model_dump(), "outputs": result}, tmp.name, logo_path=LOGO_PATH)

    return FileResponse(
        path=tmp.name,
        media_type="application/pdf",
        filename=f"Fraud_Check_{slug}.pdf",
    )


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok", "gemini_key_set": bool(os.getenv("GEMINI_API_KEY"))}
