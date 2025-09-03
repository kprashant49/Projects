import pandas as pd
import logging
import configparser
import msal
import requests
import base64
from io import BytesIO

from Snowflake_connection import get_snowflake_connection, load_config


# ---------------- Logging ----------------
def setup_logging(logfile="status_mailer.log"):
    logging.basicConfig(
        filename=logfile,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


# ---------------- Snowflake Query ----------------
def run_query(query, config):
    conn = get_snowflake_connection(config)
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()


# ---------------- Outlook Config ----------------
def load_outlook_config(path="config.ini"):
    config = configparser.ConfigParser()
    config.read(path)
    return {
        "client_id": config["OUTLOOK"]["client_id"],
        "client_secret": config["OUTLOOK"]["client_secret"],
        "tenant_id": config["OUTLOOK"]["tenant_id"],
        "sender": config["OUTLOOK"]["sender"],
        "to": [r.strip() for r in config.get("OUTLOOK", "recipients", fallback="").split(",") if r.strip()],
        "cc": [r.strip() for r in config.get("OUTLOOK", "cc", fallback="").split(",") if r.strip()],
        "bcc": [r.strip() for r in config.get("OUTLOOK", "bcc", fallback="").split(",") if r.strip()],
        # New flags
        "send_excel": config.getboolean("OUTLOOK", "send_excel", fallback=True),
        "send_pdf": config.getboolean("OUTLOOK", "send_pdf", fallback=True),
    }


# ---------------- Helper: Convert DataFrame to Attachments ----------------
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False, sheet_name="Report")
    return buffer.getvalue()

def df_to_pdf_bytes(df: pd.DataFrame) -> bytes:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    style = getSampleStyleSheet()

    # Add a title
    elements.append(Paragraph("Report", style["Title"]))

    # Convert DataFrame to list
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ]))
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()


# ---------------- Outlook Mailer ----------------
def send_mail(subject, body_html, outlook_config, attachments=None):
    """
    attachments: list of dicts { "name": "file.xlsx", "content_bytes": b"...", "mime": "application/vnd.ms-excel" }
    """
    authority = f"https://login.microsoftonline.com/{outlook_config['tenant_id']}"
    scope = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        outlook_config["client_id"],
        authority=authority,
        client_credential=outlook_config["client_secret"]
    )
    token_result = app.acquire_token_for_client(scopes=scope)
    if "access_token" not in token_result:
        raise Exception(f"Authentication failed: {token_result.get('error_description')}")

    # Recipients
    to = [{"emailAddress": {"address": e}} for e in outlook_config["to"]]
    cc = [{"emailAddress": {"address": e}} for e in outlook_config["cc"]]
    bcc = [{"emailAddress": {"address": e}} for e in outlook_config["bcc"]]

    email_msg = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "from": {"emailAddress": {"address": outlook_config["sender"]}},
            "toRecipients": to,
        }
    }
    if cc: email_msg["message"]["ccRecipients"] = cc
    if bcc: email_msg["message"]["bccRecipients"] = bcc

    # Add attachments if any
    if attachments:
        email_msg["message"]["attachments"] = []
        for att in attachments:
            email_msg["message"]["attachments"].append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": att["name"],
                "contentBytes": base64.b64encode(att["content_bytes"]).decode("utf-8"),
                "contentType": att["mime"],
            })

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{outlook_config['sender']}/sendMail",
        headers={"Authorization": f"Bearer {token_result['access_token']}"},
        json=email_msg,
    )

    if response.status_code == 202:
        logging.info("Email sent successfully")
    else:
        logging.error(f"Failed to send email: {response.status_code} {response.text}")
