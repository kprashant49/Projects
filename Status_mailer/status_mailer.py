import pandas as pd
import logging
import configparser
import msal
import requests
from Snowflake_connection import get_snowflake_connection, load_config

query = """
SELECT 'ICICI' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI

UNION ALL

SELECT 'CITI' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI

UNION ALL

SELECT 'HDFC' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC

UNION ALL

SELECT 'Saraswa' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS
"""
# ---------------- Logging ----------------
def setup_logging():
    logging.basicConfig(
        filename='status_mailer.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# ---------------- Snowflake Query ----------------
def query_to_df(query, config):
    conn = get_snowflake_connection(config)
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()


# ---------------- Outlook Mailer ----------------
def load_outlook_config(path="config.ini"):
    config = configparser.ConfigParser()
    config.read(path)
    return {
        "client_id": config["OUTLOOK"]["client_id"],
        "client_secret": config["OUTLOOK"]["client_secret"],
        "tenant_id": config["OUTLOOK"]["tenant_id"],
        "sender": config["OUTLOOK"]["sender"],
        "recipients": [
            r.strip() for r in config["OUTLOOK"]["recipients"].split(",") if r.strip()
        ],
    }

def send_outlook_mail(subject, body_html, outlook_config):
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

    # Build recipient list for Graph API
    to_recipients = [{"emailAddress": {"address": r}} for r in outlook_config["recipients"]]

    email_msg = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "from": {"emailAddress": {"address": outlook_config["sender"]}},
            "toRecipients": to_recipients,
        }
    }

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{outlook_config['sender']}/sendMail",
        headers={"Authorization": f"Bearer {token_result['access_token']}"},
        json=email_msg,
    )

    if response.status_code == 202:
        logging.info("Email sent successfully via Outlook.")
    else:
        logging.error(f"Failed to send email: {response.status_code} {response.text}")

# ---------------- Main Status Mailer ----------------
def status_mailer():
    setup_logging()
    logging.info("Starting Status Mailer (Snowflake + Outlook)")

    try:
        # Load configs
        sf_config = load_config("config.ini")
        outlook_config = load_outlook_config("config.ini")

        # Fetch query results
        df = query_to_df(query, sf_config)
        logging.info("Fetched latest transaction dates successfully.")

        # Convert DataFrame to HTML
        df_html = df.to_html(index=False, border=1, justify="center")

        # Send Outlook email
        subject = "India Cashflow Latest Transaction Report"
        body_html = f"<h3>Latest Transaction Dates per Bank</h3>{df_html}"
        send_outlook_mail(subject, body_html, outlook_config)

    except Exception as e:
        logging.error(f"Status Mailer failed: {e}")
        raise

if __name__ == "__main__":
    status_mailer()