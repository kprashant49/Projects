"""
report_generator.py — Generate a PDF AML screening report using ReportLab.

Output is written to the output/ directory (created automatically).
Logo is loaded from assets/logo.png — if missing, the header renders without it.
"""

import uuid
from datetime import datetime
from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from config import OUTPUT_DIR, LOGO_PATH, MAX_EVIDENCE_IN_REPORT


# ---------------------------------------------------------------------------
# Canvas subclass — "Page X of Y" footer
# ---------------------------------------------------------------------------

class _NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page_number(total)
            super().showPage()
        super().save()

    def _draw_page_number(self, total: int):
        self.setFont("Helvetica", 9)
        self.drawRightString(A4[0] - 40, 25, f"Page {self._pageNumber} of {total}")


# ---------------------------------------------------------------------------
# Header + Footer callback
# ---------------------------------------------------------------------------

def _draw_header_footer(canvas_obj, doc, report_id: str):
    canvas_obj.saveState()
    width, height = A4

    # Title
    canvas_obj.setFont("Helvetica-Bold", 16)
    canvas_obj.setFillColor(colors.HexColor("#0F172A"))
    canvas_obj.drawString(doc.leftMargin, height - 40, "Anti-Money Laundering Screening Report")

    # Timestamp
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.setFillColor(colors.HexColor("#475569"))
    canvas_obj.drawString(
        doc.leftMargin,
        height - 55,
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
    )

    # Divider
    canvas_obj.setStrokeColor(colors.HexColor("#DF0024"))
    canvas_obj.setLineWidth(1)
    canvas_obj.line(doc.leftMargin, height - 65, width - doc.rightMargin, height - 65)

    # Logo (optional — skipped gracefully if file is missing)
    if LOGO_PATH.exists():
        img     = ImageReader(str(LOGO_PATH))
        iw, ih  = img.getSize()
        scale   = 120 / iw
        canvas_obj.drawImage(
            str(LOGO_PATH),
            width - doc.rightMargin - iw * scale,
            height - 55,
            width=iw * scale,
            height=ih * scale,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Footer
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.setFillColor(colors.black)
    canvas_obj.drawString(doc.leftMargin, 25, f"Report ID: {report_id} | Confidential")

    canvas_obj.restoreState()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf_report(result: dict) -> str:
    """
    Build a PDF report for the given AML result dict.
    Returns the absolute path of the generated PDF file.
    """
    safe_name   = result["name"].replace(" ", "_")
    date_str    = datetime.now().strftime("%Y-%m-%d")
    report_id   = str(uuid.uuid4())[:8].upper()
    output_path = OUTPUT_DIR / f"AML_{safe_name}_{date_str}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize     = A4,
        leftMargin   = 0.75 * inch,
        rightMargin  = 0.75 * inch,
        topMargin    = 1.1  * inch,
        bottomMargin = 0.9  * inch,
    )

    styles = getSampleStyleSheet()

    section_style = ParagraphStyle(
        "Section",
        parent    = styles["Heading2"],
        fontName  = "Helvetica-Bold",
        fontSize  = 13,
        textColor = colors.HexColor("#0F172A"),
        spaceAfter = 8,
    )
    normal = ParagraphStyle(
        "NormalText",
        parent   = styles["Normal"],
        fontName = "Helvetica",
        fontSize = 10.5,
        leading  = 14,
    )
    justified = ParagraphStyle(
        "Justified",
        parent    = styles["Normal"],
        alignment = TA_JUSTIFY,
        fontName  = "Helvetica",
        fontSize  = 10.5,
        leading   = 14,
    )

    _TABLE_STYLE = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#F2F2F2")),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
        ("GRID",          (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])

    elements = []

    # ---- Customer Input Details ----
    elements.append(Paragraph("Customer Input Details", section_style))
    input_table = Table(
        [["Field", "Value"], ["Name", result["name"]], ["Place", result["place"]]],
        colWidths=[2.2 * inch, 4.3 * inch],
    )
    input_table.setStyle(_TABLE_STYLE)
    elements.append(input_table)
    elements.append(Spacer(1, 20))

    # ---- Fraud Analysis Results ----
    elements.append(Paragraph("Fraud Analysis Results", section_style))
    breakdown = result["score_breakdown"]
    result_table = Table(
        [
            ["Metric",          "Value"],
            ["Fraud Hits",      breakdown["fraud_hits"]],
            ["Fraud Score",     breakdown["fraud_score"]],
            ["Sanctions Match", breakdown["sanctions_match"]],
            ["Sanctions Score", breakdown["sanctions_score"]],
            ["PEP Hits",        breakdown["pep_hits"]],
            ["PEP Score",       breakdown["pep_score"]],
            ["Mobile Hits",     breakdown.get("mobile_hits", 0)],
            ["Mobile Score",    breakdown.get("mobile_score", 0)],
            ["PAN Hits",        breakdown.get("pan_hits", 0)],
            ["PAN Score",       breakdown.get("pan_score", 0)],
            ["Total Score",     breakdown["total_score"]],
            ["Risk Level",      result["risk_category"]],
        ],
        colWidths=[3.5 * inch, 3.0 * inch],
    )
    result_table.setStyle(_TABLE_STYLE)
    elements.append(result_table)
    elements.append(Spacer(1, 20))

    # ---- Compliance Summary ----
    elements.append(Paragraph("Compliance Summary", section_style))
    # Replace rupee symbol for basic Helvetica compatibility
    summary_text = result["summary"].replace("₹", "Rs.")
    elements.append(Paragraph(summary_text, justified))
    elements.append(PageBreak())

    # ---- Evidence Section ----
    elements.append(Paragraph("Evidence Collected", section_style))
    elements.append(Spacer(1, 6))

    for item in result["evidence"][:MAX_EVIDENCE_IN_REPORT]:
        text = f"{item.get('source', 'Unknown')} — {item.get('title', '')}"
        elements.append(Paragraph(text, normal))
        elements.append(Spacer(1, 4))

    # ---- Build ----
    doc.build(
        elements,
        onFirstPage  = lambda c, d: _draw_header_footer(c, d, report_id),
        onLaterPages = lambda c, d: _draw_header_footer(c, d, report_id),
        canvasmaker  = _NumberedCanvas,
    )

    return str(output_path)
