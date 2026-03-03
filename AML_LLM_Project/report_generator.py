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
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas


# ---------------------------------------------------
# Canvas class for "Page X of Y"
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
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 9)
        self.drawRightString(A4[0] - 40, 25, page_text)


# ---------------------------------------------------
# Main Report Generator
# ---------------------------------------------------
def generate_pdf_report(result, logo_path=r"D:\Projects\AML_LLM_Project\PAI_logo_inline.png"):

    # Auto filename
    safe_name = result["name"].replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = rf"C:\Users\kpras\Desktop\ALM_{safe_name}_{date_str}.pdf"

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=75,   # Reduced header height
        bottomMargin=60
    )

    elements = []
    styles = getSampleStyleSheet()

    # Section Header Style
    styles.add(ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#003366"),
        spaceAfter=6
    ))

    # Justified style for compliance narrative
    justified_style = ParagraphStyle(
        name="Justified",
        parent=styles["Normal"],
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        fontSize=10,
        leading=14
    )

    normal = styles["Normal"]

    # ---------------------------------------------------
    # Basic Information
    # ---------------------------------------------------
    elements.append(Paragraph(f"<b>Name:</b> {result['name']}", normal))
    elements.append(Paragraph(f"<b>Place:</b> {result['place']}", normal))
    elements.append(Paragraph(f"<b>Generated On:</b> {datetime.now()}", normal))
    elements.append(Spacer(1, 12))

    # ---------------------------------------------------
    # Risk Color Band
    # ---------------------------------------------------
    category = result["risk_category"]

    if category == "High":
        band_color = colors.red
    elif category == "Medium":
        band_color = colors.orange
    else:
        band_color = colors.green

    band_table = Table(
        [[f"RISK LEVEL: {category.upper()}"]],
        colWidths=[6 * inch]
    )

    band_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), band_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
    ]))

    elements.append(band_table)
    elements.append(Spacer(1, 12))

    # ---------------------------------------------------
    # Risk Summary
    # ---------------------------------------------------
    elements.append(Paragraph("Risk Summary", styles["SectionHeader"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"Risk Score: {result['risk_score']}", normal))
    elements.append(Spacer(1, 8))

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
    ]

    table = Table(table_data, colWidths=[3.5 * inch, 2.5 * inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E6EEF7")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 18))

    # ---------------------------------------------------
    # Compliance Narrative
    # ---------------------------------------------------
    elements.append(Paragraph("Compliance Narrative", styles["SectionHeader"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(result["summary"], justified_style))
    elements.append(PageBreak())

    # ---------------------------------------------------
    # Evidence Section
    # ---------------------------------------------------
    elements.append(Paragraph("Evidence Collected", styles["SectionHeader"]))
    elements.append(Spacer(1, 8))

    for item in result["evidence"][:20]:
        text = f"{item.get('source')} — {item.get('title')}"
        elements.append(Paragraph(text, normal))
        elements.append(Spacer(1, 4))

    # ---------------------------------------------------
    # Header + Footer (Canvas Layer)
    # ---------------------------------------------------
    report_id = str(uuid.uuid4())[:8].upper()

    def add_header_footer(canvas_obj, doc_obj):

        canvas_obj.saveState()
        page_width, page_height = A4

        # Title
        canvas_obj.setFont("Helvetica-Bold", 14)
        canvas_obj.drawString(
            40,
            page_height - 35,
            "Anti-Money Laundering Screening Report"
        )

        # Corporate blue accent line
        canvas_obj.setStrokeColor(colors.HexColor("#003366"))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(
            40,
            page_height - 45,
            page_width - 40,
            page_height - 45
        )

        # Logo (absolute top-right)
        if os.path.exists(logo_path):
            img = ImageReader(logo_path)
            img_width, img_height = img.getSize()

            desired_width = 85
            aspect = img_height / img_width
            desired_height = desired_width * aspect

            x_position = page_width - desired_width - 20
            y_position = page_height - desired_height - 20

            canvas_obj.drawImage(
                logo_path,
                x_position,
                y_position,
                width=desired_width,
                height=desired_height,
                preserveAspectRatio=True,
                mask='auto'
            )

        # Footer Left
        footer_text = f"Report ID: {report_id} | Confidential"
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(40, 25, footer_text)

        canvas_obj.restoreState()

    doc.build(
        elements,
        onFirstPage=add_header_footer,
        onLaterPages=add_header_footer,
        canvasmaker=NumberedCanvas
    )

    return output_path