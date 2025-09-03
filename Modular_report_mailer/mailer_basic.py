import pandas as pd
import logging
import configparser
import msal
import requests
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
    }

# ---------------- Outlook Mailer ----------------
def send_mail(subject, body_html, outlook_config):
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

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{outlook_config['sender']}/sendMail",
        headers={"Authorization": f"Bearer {token_result['access_token']}"},
        json=email_msg,
    )

    if response.status_code == 202:
        logging.info("✅ Email sent successfully")
    else:
        logging.error(f"❌ Failed to send email: {response.status_code} {response.text}")
