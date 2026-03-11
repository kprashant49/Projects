import os
import uuid
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


# ---------------------------------------------------
# Canvas for Page X of Y
# ---------------------------------------------------

class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)

        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(total_pages)
            super().showPage()

        super().save()

    def draw_page_number(self, page_count):
        text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 9)
        self.drawRightString(A4[0] - 40, 25, text)


# ---------------------------------------------------
# Header + Footer
# ---------------------------------------------------

def draw_header_footer(canvas_obj, doc, logo_path, report_id):

    canvas_obj.saveState()

    width, height = A4

    # Title
    canvas_obj.setFont("Helvetica-Bold", 16)
    canvas_obj.setFillColor(colors.HexColor("#0F172A"))
    canvas_obj.drawString(
        doc.leftMargin,
        height - 40,
        "Anti-Money Laundering Screening Report"
    )

    # Generated timestamp
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.setFillColor(colors.HexColor("#475569"))

    time_text = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    canvas_obj.drawString(
        doc.leftMargin,
        height - 55,
        f"Generated on: {time_text}"
    )

    # Divider line
    canvas_obj.setStrokeColor(colors.HexColor("#DF0024"))
    canvas_obj.setLineWidth(1)

    canvas_obj.line(
        doc.leftMargin,
        height - 65,
        width - doc.rightMargin,
        height - 65
    )

    # Logo
    if os.path.exists(logo_path):

        img = ImageReader(logo_path)

        iw, ih = img.getSize()

        max_w = 120
        scale = max_w / iw

        w = iw * scale
        h = ih * scale

        canvas_obj.drawImage(
            logo_path,
            width - doc.rightMargin - w,
            height - 55,
            width=w,
            height=h,
            preserveAspectRatio=True,
            mask="auto"
        )

    # Footer text
    canvas_obj.setFont("Helvetica", 9)

    canvas_obj.drawString(
        doc.leftMargin,
        25,
        f"Report ID: {report_id} | Confidential"
    )

    canvas_obj.restoreState()


# ---------------------------------------------------
# Main Generator
# ---------------------------------------------------

def generate_pdf_report(
        result,
        logo_path=r"D:\Projects\AML_LLM_Project\PAI_logo_inline.png"
):

    safe_name = result["name"].replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")

    output_path = rf"C:\Users\kpras\Desktop\AML_{safe_name}_{date_str}.pdf"

    report_id = str(uuid.uuid4())[:8].upper()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=1.1 * inch,
        bottomMargin=0.9 * inch
    )

    styles = getSampleStyleSheet()

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8
    )

    normal = ParagraphStyle(
        "NormalText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14
    )

    justified = ParagraphStyle(
        "Justified",
        parent=styles["Normal"],
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        fontSize=10.5,
        leading=14
    )

    elements = []

    # ---------------------------------------------------
    # Customer Inputs
    # ---------------------------------------------------

    elements.append(Paragraph("Customer Input Details", section_style))

    input_rows = [
        ["Field", "Value"],
        ["Name", result["name"]],
        ["Place", result["place"]]
    ]

    input_table = Table(input_rows, colWidths=[2.2 * inch, 4.3 * inch])

    input_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#FAFAFA")]),

        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),

        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

    ]))

    elements.append(input_table)
    elements.append(Spacer(1, 20))


    # ---------------------------------------------------
    # Fraud Analysis Results
    # ---------------------------------------------------

    elements.append(Paragraph("Fraud Analysis Results", section_style))

    breakdown = result["score_breakdown"]

    table_data = [
        ["Metric", "Value"],

        ["Fraud Hits", breakdown["fraud_hits"]],
        ["Fraud Score", breakdown["fraud_score"]],

        ["Sanctions Match", breakdown["sanctions_match"]],
        ["Sanctions Score", breakdown["sanctions_score"]],

        ["PEP Hits", breakdown["pep_hits"]],
        ["PEP Score", breakdown["pep_score"]],

        ["Mobile Hits", breakdown.get("mobile_hits", 0)],
        ["Mobile Score", breakdown.get("mobile_score", 0)],

        ["PAN Hits", breakdown.get("pan_hits", 0)],
        ["PAN Score", breakdown.get("pan_score", 0)],

        ["Total Score", breakdown["total_score"]],

        ["Risk Level", result["risk_category"]]
    ]

    result_table = Table(table_data, colWidths=[3.5 * inch, 3 * inch])

    result_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F2F2")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#FAFAFA")]),

        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E5E5")),

        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)

    ]))

    elements.append(result_table)
    elements.append(Spacer(1, 20))

    # ---------------------------------------------------
    # Websearch Summary
    # ---------------------------------------------------

    elements.append(Paragraph("Websearch Summary", section_style))

    summary_text = result["summary"].replace("₹", "Rs.")

    elements.append(Paragraph(summary_text, justified))
    elements.append(PageBreak())

    # ---------------------------------------------------
    # Evidence Section
    # ---------------------------------------------------

    elements.append(Paragraph("Evidence Collected", section_style))
    elements.append(Spacer(1, 6))

    for item in result["evidence"][:20]:

        text = f"{item.get('source')} — {item.get('title')}"

        elements.append(Paragraph(text, normal))
        elements.append(Spacer(1, 4))

    # ---------------------------------------------------
    # Build Document
    # ---------------------------------------------------

    doc.build(
        elements,
        onFirstPage=lambda c, d: draw_header_footer(c, d, logo_path, report_id),
        onLaterPages=lambda c, d: draw_header_footer(c, d, logo_path, report_id),
        canvasmaker=NumberedCanvas
    )

    return output_path