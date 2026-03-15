"""
api.py
──────
Gemini Fraud Check — single-file FastAPI app.
All logic (Gemini call + PDF generation) is inlined here.

Run:
    pip install fastapi uvicorn google-genai reportlab
    set GEMINI_API_KEY=your_gemini_key    (Windows)
    set APP_API_KEY=your_secret_key       (Windows)
    export GEMINI_API_KEY=your_gemini_key (Linux/Mac)
    export APP_API_KEY=your_secret_key    (Linux/Mac)
    uvicorn api:app --reload --port 8000

All POST endpoints require the header:
    X-API-Key: your_secret_key
"""

import os
import re
import json
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from reportlab.lib import pagesizes, colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


# =========================================================
# Configuration  ← Edit these values for your environment
# =========================================================
GEMINI_MODEL = "gemini-2.5-flash"
LOGO_PATH    = r"D:\Projects\ALM_Project_Slim\PAI_logo_inline.png"  # "" to skip


# =========================================================
# API Key Protection
# =========================================================
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_key(key: str = Security(_api_key_header)):
    """Dependency — rejects requests that don't carry the correct X-API-Key header."""
    expected = os.getenv("APP_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=500, detail="APP_API_KEY is not configured on the server.")
    if key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")


# =========================================================
# 1. Clean & Parse Gemini JSON Safely
# =========================================================
def clean_and_parse_json(response_text: str) -> dict:
    cleaned = re.sub(r"```json|```", "", response_text).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No valid JSON in model response.\n\nRaw:\n{response_text}")
    return json.loads(match.group(0))


# =========================================================
# 2. Gemini Fraud Check
# =========================================================
def run_gemini_fraud_check(
    customer_name: str, place: str, mobile: str, company: str
) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

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

    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
    response = client.models.generate_content(
        model=GEMINI_MODEL, contents=prompt, config=config
    )
    return clean_and_parse_json(response.text)


# =========================================================
# 3. Shared Table Style
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
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

    LEFT_MARGIN = RIGHT_MARGIN = 0.75 * inch
    AVAIL_W = pagesizes.A4[0] - LEFT_MARGIN - RIGHT_MARGIN
    COL1_W  = 2.2 * inch
    COL2_W  = AVAIL_W - COL1_W

    doc = SimpleDocTemplate(
        file_path, pagesize=pagesizes.A4,
        leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN,
        topMargin=1 * inch, bottomMargin=0.8 * inch,
    )

    styles    = getSampleStyleSheet()
    h2_style  = ParagraphStyle("H2", parent=styles["Heading2"],
                    fontName="Helvetica-Bold", fontSize=14, leading=18,
                    textColor=colors.HexColor("#0F172A"), spaceBefore=12, spaceAfter=8)
    sum_style = ParagraphStyle("Sum", parent=styles["Normal"],
                    fontName="Helvetica", fontSize=10.5, leading=15,
                    textColor=colors.HexColor("#0F172A"), alignment=TA_JUSTIFY)

    def draw_header_footer(canv: canvas.Canvas, _doc):
        w, h    = pagesizes.A4
        hdr_y   = h - 0.6 * inch
        left_x  = doc.leftMargin
        right_x = w - doc.rightMargin

        canv.setFont("Helvetica-Bold", 16)
        canv.setFillColor(colors.HexColor("#0F172A"))
        canv.drawString(left_x, hdr_y, "Web Fraud Check Report  ✦ Powered by Gemini AI")

        canv.setFont("Helvetica", 9.5)
        canv.setFillColor(colors.HexColor("#475569"))
        canv.drawString(left_x, hdr_y - 14,
                        f"Report generated on: {datetime.now().strftime('%d-%m-%Y  %H:%M:%S')}")

        if logo_path and os.path.isfile(logo_path):
            try:
                ir = ImageReader(logo_path)
                iw, ih = ir.getSize()
                scale = min(120 / iw, 36 / ih)
                lw, lh = iw * scale, ih * scale
                canv.drawImage(logo_path, right_x - lw, hdr_y - (lh - 6),
                               width=lw, height=lh, preserveAspectRatio=True, mask="auto")
            except Exception:
                pass

        canv.setStrokeColor(colors.HexColor("#DF0024"))
        canv.setLineWidth(0.8)
        canv.line(left_x, hdr_y - 22, right_x, hdr_y - 22)

        canv.setFont("Helvetica", 9)
        canv.setFillColor(colors.HexColor("#475569"))
        canv.drawRightString(right_x, 0.5 * inch, f"Page {canv.getPageNumber()}")

    inputs  = data.get("inputs")  or {}
    outputs = data.get("outputs") or {}

    RISK_BG  = {"low": colors.HexColor("#DCFCE7"), "medium": colors.HexColor("#FEF3C7"),
                "high": colors.HexColor("#FEE2E2")}
    RISK_TXT = {"low": colors.HexColor("#166534"), "medium": colors.HexColor("#92400E"),
                "high": colors.HexColor("#991B1B")}

    result_rows    = [["Metric", "Value"]]
    risk_row_index = None
    for k, v in outputs.items():
        if k == "Summary":
            continue
        if k == "Risk Category":
            risk_row_index = len(result_rows)
        result_rows.append([str(k), "" if v is None else str(v)])

    results_ts = _make_table_style()
    if risk_row_index is not None:
        rv = (outputs.get("Risk Category") or "").strip().lower()
        results_ts.add("BACKGROUND", (0, risk_row_index), (-1, risk_row_index),
                       RISK_BG.get(rv,  colors.HexColor("#F2F2F2")))
        results_ts.add("TEXTCOLOR",  (0, risk_row_index), (-1, risk_row_index),
                       RISK_TXT.get(rv, colors.HexColor("#222222")))
        results_ts.add("FONTNAME",   (0, risk_row_index), (-1, risk_row_index), "Helvetica-Bold")

    input_rows  = [["Field", "Value"]] + [
        [str(k), "" if v is None else str(v)] for k, v in inputs.items()
    ]
    inputs_tbl  = Table(input_rows,  colWidths=[COL1_W, COL2_W])
    results_tbl = Table(result_rows, colWidths=[COL1_W, COL2_W])
    inputs_tbl.setStyle(_make_table_style())
    results_tbl.setStyle(results_ts)

    summary_text = (outputs.get("Summary") or "—").replace("₹", "Rs.")

    elements = [
        Spacer(1, 0.1 * inch),
        Paragraph("Customer Input Details", h2_style),
        Spacer(1, 0.06 * inch),
        inputs_tbl,
        Spacer(1, 0.25 * inch),
        Paragraph("Fraud Analysis Results", h2_style),
        Spacer(1, 0.06 * inch),
        results_tbl,
        Spacer(1, 0.25 * inch),
        Paragraph("Web Search Summary", h2_style),
        Spacer(1, 0.06 * inch),
        Paragraph(summary_text, sum_style),
    ]

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


@app.get("/health", include_in_schema=False)
def health():
    return {
        "status": "ok",
        "gemini_key_set": bool(os.getenv("GEMINI_API_KEY")),
        "app_key_set":    bool(os.getenv("APP_API_KEY")),
    }


@app.post("/check", summary="Fraud check — returns JSON", response_class=JSONResponse,
          dependencies=[Depends(verify_key)])
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


@app.post("/check/report", summary="Fraud check — returns PDF", response_class=FileResponse,
          dependencies=[Depends(verify_key)])
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

    generate_pdf({"inputs": req.model_dump(), "outputs": result},
                 tmp.name, logo_path=LOGO_PATH)

    return FileResponse(
        path=tmp.name,
        media_type="application/pdf",
        filename=f"Fraud_Check_{slug}.pdf",
    )