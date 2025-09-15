import pandas as pd
import logging
import configparser
import msal
import requests
from Snowflake_connection import get_snowflake_connection, load_config
from datetime import datetime, timedelta

query = """
SELECT 
    'Pepper' AS "Entity",
    'Citibank' AS "Bank",
     TO_VARCHAR(MAX(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS'))),'DD/MM/YYYY') AS "Latest Transaction Date",
     'Rs. '|| (SELECT BALANCE_INR FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI WHERE GLOBAL_RANK = (SELECT max(GLOBAL_RANK) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI)) AS "Closing Balance",
     TO_VARCHAR(MAX(TO_DATE(lot_dt, 'DD-MON-YY')),'DD/MM/YYYY') AS "Last Data Load Date",
     (SELECT COUNT(NEW_CATEGORY) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI WHERE NEW_CATEGORY = 'Other') AS "Unmapped Transaction(s)"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI

UNION ALL

SELECT 
    'Pepper' AS "Entity",
    'HDFC Bank' AS "Bank",
    TO_VARCHAR(MAX(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS'))),'DD/MM/YYYY') AS "Latest Transaction Date",
    'Rs. '|| (SELECT BALANCE_INR FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC WHERE GLOBAL_RANK = (SELECT max(GLOBAL_RANK) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC)) AS "Closing Balance",
    TO_VARCHAR(MAX(TO_DATE(lot_dt, 'DD-MON-YY')),'DD/MM/YYYY') AS "Last Data Load Date",
    (SELECT COUNT(NEW_CATEGORY) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC WHERE NEW_CATEGORY = 'Other') AS "Unmapped Transaction(s)"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC

UNION ALL

SELECT 
    'Rieom' AS "Entity",
    'ICICI Bank' AS "Bank",
     TO_VARCHAR(MAX(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS'))),'DD/MM/YYYY') AS "Latest Transaction Date",
     'Rs. '|| (SELECT BALANCE_INR FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI WHERE GLOBAL_RANK = (SELECT max(GLOBAL_RANK) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI)) AS "Closing Balance",
     TO_VARCHAR(MAX(TO_DATE(lot_dt, 'DD-MON-YY')),'DD/MM/YYYY') AS "Last Data Load Date",
     (SELECT COUNT(NEW_CATEGORY) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI WHERE NEW_CATEGORY = 'Other') AS "Unmapped Transaction(s)"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI

UNION ALL

SELECT 
    'Rieom' AS "Entity",
    'Saraswat Bank' AS "Bank",
    TO_VARCHAR(MAX(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS'))),'DD/MM/YYYY') AS "Latest Transaction Date",
    'Rs. '|| (SELECT BALANCE_INR FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS WHERE GLOBAL_RANK = (SELECT max(GLOBAL_RANK) FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS)) AS "Closing Balance",
    TO_VARCHAR(MAX(TO_DATE(lot_dt, 'DD-MON-YY')),'DD/MM/YYYY') AS "Last Data Load Date",
    (SELECT COUNT(NEW_CATEGORY)FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS WHERE NEW_CATEGORY = 'Other') AS "Unmapped Transaction(s)"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS;
"""

second_query = """
SELECT
    'Pepper' AS "Entity",
    'Citibank' AS "Bank",
    TO_VARCHAR(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS')),'DD/MM/YYYY') AS "Transaction Date",
    TRANSACTION_REMARKS AS "Transaction Remarks",
    TRANSACTION_TYPE AS "Transaction Type"
    FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI
    WHERE NEW_CATEGORY = 'Other'

UNION ALL

SELECT 
    'Pepper' AS "Entity",
    'HDFC Bank' AS "Bank",
    TO_VARCHAR(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS')),'DD/MM/YYYY') AS "Transaction Date",
    TRANSACTION_REMARKS AS "Transaction Remarks",
    TRANSACTION_TYPE AS "Transaction Type"
    FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC
    WHERE NEW_CATEGORY = 'Other'

UNION ALL

SELECT
    'Rieom' AS "Entity",
    'ICICI Bank' AS "Bank",
    TO_VARCHAR(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS')),'DD/MM/YYYY') AS "Transaction Date",
    TRANSACTION_REMARKS AS "Transaction Remarks",
    TRANSACTION_TYPE AS "Transaction Type"
    FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI
    WHERE NEW_CATEGORY = 'Other'

UNION ALL

SELECT
    'Rieom' AS "Entity",
    'Saraswat Bank' AS "Bank",
    TO_VARCHAR(TO_DATE(TO_TIMESTAMP(SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 1) || ' ' ||SPLIT_PART(TRANSACTION_POSTED_DATE, ' ', 2),'DD/MM/YYYY HH24:MI:SS')),'DD/MM/YYYY') AS "Transaction Date",
    TRANSACTION_REMARKS AS "Transaction Remarks",
    TRANSACTION_TYPE AS "Transaction Type"
    FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS
    WHERE NEW_CATEGORY = 'Other'
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
        "to": [r.strip() for r in config.get("OUTLOOK", "recipients", fallback="").split(",") if r.strip()],
        "cc": [r.strip() for r in config.get("OUTLOOK", "cc", fallback="").split(",") if r.strip()],
        "bcc": [r.strip() for r in config.get("OUTLOOK", "bcc", fallback="").split(",") if r.strip()],
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

    # Build recipients list
    to_recipients = [{"emailAddress": {"address": email}} for email in outlook_config["to"]]
    cc_recipients = [{"emailAddress": {"address": email}} for email in outlook_config["cc"]]
    bcc_recipients = [{"emailAddress": {"address": email}} for email in outlook_config["bcc"]]

    email_msg = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "from": {"emailAddress": {"address": outlook_config["sender"]}},
            "toRecipients": to_recipients,
        }
    }

    if cc_recipients:
        email_msg["message"]["ccRecipients"] = cc_recipients
    if bcc_recipients:
        email_msg["message"]["bccRecipients"] = bcc_recipients

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{outlook_config['sender']}/sendMail",
        headers={"Authorization": f"Bearer {token_result['access_token']}"},
        json=email_msg,
    )

    if response.status_code == 202:
        logging.info("Email sent successfully via Outlook.")
    else:
        logging.error(f"Failed to send email: {response.status_code} {response.text}")

# ---------------- Highlighting ----------------
def highlight_last_load_date(df: pd.DataFrame) -> str:
    """
    Returns HTML table with:
    - 'Last Data Load Date' formatted as DD/MM/YYYY
    - Colour scheme:
        * Today or yesterday → no colour
        * Older than yesterday but within last 3 days → orange
        * Older than 3 days → red
    - Borders and no index column
    """

    # Convert safely to datetime
    df = df.copy()
    df["Last Data Load Date"] = pd.to_datetime(df["Last Data Load Date"], format="%d/%m/%Y", errors="coerce")

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    fixed_days_ago = today - timedelta(days=5)

    # Apply formatting + inline HTML styles
    def format_and_colour(val):
        if pd.isna(val):
            return '<span style="color:red; font-weight:bold;">Invalid</span>'
        date_val = val.date()
        formatted = val.strftime("%d/%m/%Y")

        if date_val in (today, yesterday):
            return formatted  # no colour
        elif fixed_days_ago < date_val < yesterday:
            return f'<span style="color:brown; font-weight:bold;">{formatted}</span>'
        elif date_val <= fixed_days_ago:
            return f'<span style="color:red; font-weight:bold;">{formatted}</span>'
        return formatted

    df["Last Data Load Date"] = df["Last Data Load Date"].apply(format_and_colour)

    # Convert to HTML with borders & no index
    return df.to_html(escape=False, index=False, border=1, justify="center")

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
        df2 = query_to_df(second_query, sf_config)
        logging.info("Fetched unmapped records successfully.")

        # Convert DataFrame to HTML
        # df_html = df.to_html(index=False, border=1, justify="center")
        df_html = highlight_last_load_date(df)
        subject = "India Cashbook Latest Transaction Report"
        body_html = f"""
                <p>Dear All,</p>
                <p>Please find below the latest transaction dates for each bank.</p>
                {df_html}
                """

        # Add unmapped section only if df2 has rows
        if not df2.empty:
            subject = "India Cashbook Latest Transaction Report - Mapping details required"
            df2_html = df2.to_html(index=False, border=1, justify="center")
            body_html += f"""
                        <p>Please find below the unmapped transaction(s).
                        <br>Kindly check and share the mapping details with us.</p>
                        {df2_html}
                        """

        body_html += """
                    <p>Regards,<br>D&A Team</p>
                    """
        
        # Send Outlook email
        # subject = "India Cashbook Latest Transaction Report"
        send_outlook_mail(subject, body_html, outlook_config)

    except Exception as e:
        logging.error(f"Status Mailer failed: {e}")
        raise

if __name__ == "__main__":
    status_mailer()