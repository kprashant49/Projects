import logging
import requests
import base64
from graph_auth import get_graph_token
from secure_config import load_secure_config


def send_outlook_mail(subject, html_body, outlook, attachments=None):
    try:
        logging.info("Sending Outlook email")

        token = get_graph_token(
            outlook["client_id"],
            outlook["client_secret"],
            outlook["tenant_id"]
        )

        def recipients(lst):
            return [{"emailAddress": {"address": e}} for e in lst]

        message = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": recipients(outlook["to"])
        }

        if outlook.get("cc"):
            message["ccRecipients"] = recipients(outlook["cc"])
        if outlook.get("bcc"):
            message["bccRecipients"] = recipients(outlook["bcc"])

        if attachments:
            message["attachments"] = []

            for name, path in attachments:
                with open(path, "rb") as f:
                    content = base64.b64encode(f.read()).decode()

                message["attachments"].append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": name,
                    "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "contentBytes": content
                })

        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{outlook['sender']}/sendMail",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"message": message, "saveToSentItems": True}
        )

        if response.status_code != 202:
            raise Exception(response.text)

        logging.info("Email sent successfully")

    except Exception as e:
        logging.error(f"Email send failed: {e}")
        raise

def send_email(html_body):
    config = load_secure_config()
    outlook = config["outlook"]
    send_outlook_mail(outlook["subject"], html_body, outlook)

def send_failure_alert(subject, error_message):
    config = load_secure_config()
    outlook = config["outlook"].copy()
    alerts = config["alerts"]

    html = f"""
    <html>
    <body>
        <h3 style="color:red;">Job Failure Alert</h3>
        <pre>{error_message}</pre>
    </body>
    </html>
    """

    outlook["to"] = alerts["to"]
    outlook["cc"] = alerts.get("cc", [])
    outlook["bcc"] = alerts.get("bcc", [])

    send_outlook_mail(f"FAILURE: {subject}", html, outlook)
