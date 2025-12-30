import json
import logging
import requests
from graph_auth import get_graph_token
import base64


def load_outlook_config(path="config.json"):
    with open(path) as f:
        return json.load(f)["outlook"]


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

        if outlook["cc"]:
            message["ccRecipients"] = recipients(outlook["cc"])
        if outlook["bcc"]:
            message["bccRecipients"] = recipients(outlook["bcc"])

        # Attachments (Excel)
        attach_list = []
        if attachments:
            for name, path in attachments:
                with open(path, "rb") as f:
                    attach_list.append({
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": name,
                        "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "contentBytes": base64.b64encode(f.read()).decode("utf-8")
                    })

            message["attachments"] = attach_list

        payload = {"message": message, "saveToSentItems": "true"}

        response = requests.post(
            f"https://graph.microsoft.com/v1.0/users/{outlook['sender']}/sendMail",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if response.status_code != 202:
            raise Exception(response.text)

        logging.info("Email sent successfully")

    except Exception as e:
        logging.error(f"Email send failed: {e}")
        raise

def send_email(html_body):
    outlook = load_outlook_config()
    send_outlook_mail(outlook["subject"], html_body, outlook)
