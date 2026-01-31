import logging
import requests
import base64
from graph_auth import get_graph_token
from secure_config import load_secure_config


def send_outlook_mail(subject, html_body, outlook, attachments=None):
    """
    Sends an email via Microsoft Graph.
    outlook = { to, cc, bcc }
    sender & Graph credentials are loaded globally from secure config.
    """
    try:
        logging.info("Sending Outlook email")

        config = load_secure_config()

        # -------------------------
        # Graph authentication (SECRETS)
        # -------------------------
        graph = config["outlook"]  # from secrets.enc
        token = get_graph_token(
            graph["client_id"],
            graph["client_secret"],
            graph["tenant_id"]
        )

        # -------------------------
        # Global sender
        # -------------------------
        sender = config["mailer"]["sender"]

        def recipients(lst):
            return [{"emailAddress": {"address": e}} for e in lst]

        # -------------------------
        # Message body
        # -------------------------
        message = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": recipients(outlook["to"])
        }

        if outlook.get("cc"):
            message["ccRecipients"] = recipients(outlook["cc"])
        if outlook.get("bcc"):
            message["bccRecipients"] = recipients(outlook["bcc"])

        # -------------------------
        # Attachments (optional)
        # -------------------------
        if attachments:
            message["attachments"] = []

            for name, path in attachments:
                with open(path, "rb") as f:
                    content = base64.b64encode(f.read()).decode("utf-8")

                message["attachments"].append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": name,
                    "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "contentBytes": content
                })

        # -------------------------
        # Send mail
        # -------------------------
        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail",
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


def send_failure_alert(subject, error_message):
    """
    Sends failure alert email to admins
    """
    config = load_secure_config()
    alerts = config["alerts"]

    html = f"""
    <html>
    <body>
        <h3 style="color:red;">Job Failure Alert</h3>
        <pre>{error_message}</pre>
    </body>
    </html>
    """

    outlook = {
        "to": alerts["to"],
        "cc": alerts.get("cc", []),
        "bcc": alerts.get("bcc", [])
    }

    send_outlook_mail(
        subject=f"FAILURE: {subject}",
        html_body=html,
        outlook=outlook
    )
