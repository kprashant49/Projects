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


def generate_pdf_report(result, logo_path=r"D:\Projects\AML_LLM_Project\PAI_logo_inline.png"):

    # -------------------------------
    # Auto filename
    # -------------------------------
    safe_name = result["name"].replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = rf"C:\Users\kpras\Desktop\ALM_{safe_name}_{date_str}.pdf"

    # -------------------------------
    # Create document
    # -------------------------------
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=90,   # Push content below header
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

    # Justified paragraph style for summary
    justified_style = ParagraphStyle(
        name="Justified",
        parent=styles["Normal"],
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        fontSize=10,
        leading=14
    )

    normal = styles["Normal"]

    # -------------------------------
    # Basic Info
    # -------------------------------
    elements.append(Paragraph(f"<b>Name:</b> {result['name']}", normal))
    elements.append(Paragraph(f"<b>Place:</b> {result['place']}", normal))
    elements.append(Paragraph(f"<b>Generated On:</b> {datetime.now()}", normal))
    elements.append(Spacer(1, 15))

    # -------------------------------
    # Risk Color Band
    # -------------------------------
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
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))

    elements.append(band_table)
    elements.append(Spacer(1, 15))

    # -------------------------------
    # Risk Summary Section
    # -------------------------------
    elements.append(Paragraph("Risk Summary", styles["SectionHeader"]))
    elements.append(Spacer(1, 5))

    elements.append(Paragraph(f"Risk Score: {result['risk_score']}", normal))
    elements.append(Spacer(1, 10))

    breakdown = result["score_breakdown"]

    table_data = [
        ["Metric", "Value"],
        ["Fraud Hits", breakdown["fraud_hits"]],
        ["Fraud Score", breakdown["fraud_score"]],
        ["Sanctions Match", breakdown["sanctions_match"]],
        ["Sanctions Score", breakdown["sanctions_score"]],
        ["PEP Hits", breakdown["pep_hits"]],
        ["PEP Score", breakdown["pep_score"]],
        ["Total Score", breakdown["total_score"]],
    ]

    table = Table(table_data, colWidths=[3.5 * inch, 2.5 * inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # -------------------------------
    # Compliance Narrative (JUSTIFIED)
    # -------------------------------
    elements.append(Paragraph("Compliance Narrative", styles["SectionHeader"]))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(result["summary"], justified_style))
    elements.append(PageBreak())

    # -------------------------------
    # Evidence Section
    # -------------------------------
    elements.append(Paragraph("Evidence Collected", styles["SectionHeader"]))
    elements.append(Spacer(1, 10))

    for item in result["evidence"][:20]:
        text = f"{item.get('source')} — {item.get('title')}"
        elements.append(Paragraph(text, normal))
        elements.append(Spacer(1, 4))

    # -------------------------------
    # Header + Footer (Canvas)
    # -------------------------------
    report_id = str(uuid.uuid4())[:8].upper()

    def add_header_footer(canvas, doc):

        canvas.saveState()
        page_width, page_height = A4

        # ---- Title (Single Line Left) ----
        canvas.setFont("Helvetica-Bold", 15)
        canvas.drawString(
            40,
            page_height - 40,
            "Anti-Money Laundering Screening Report"
        )

        # ---- Logo (Top Right Absolute) ----
        if os.path.exists(logo_path):
            img = ImageReader(logo_path)
            img_width, img_height = img.getSize()

            desired_width = 90
            aspect = img_height / img_width
            desired_height = desired_width * aspect

            x_position = page_width - desired_width - 20
            y_position = page_height - desired_height - 20

            canvas.drawImage(
                logo_path,
                x_position,
                y_position,
                width=desired_width,
                height=desired_height,
                preserveAspectRatio=True,
                mask='auto'
            )

        # ---- Separator Line ----
        canvas.setLineWidth(1)
        canvas.setStrokeColor(colors.grey)
        canvas.line(
            40,
            page_height - 55,
            page_width - 40,
            page_height - 55
        )

        # ---- Footer ----
        footer_text = f"Report ID: {report_id} | Confidential"
        canvas.setFont("Helvetica", 9)
        canvas.drawString(40, 25, footer_text)

        canvas.restoreState()

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    return output_path