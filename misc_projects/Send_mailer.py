import smtplib
from email.message import EmailMessage
import mimetypes

def send_email_with_attachment(sender, recipient, subject, body, file_path, app_password):
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    # Read the Excel file
    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name
        mime_type, _ = mimetypes.guess_type(file_name)
        maintype, subtype = mime_type.split('/')

    # Add attachment
    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)

    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)
        print("Email sent successfully!")

# Example usage
send_email_with_attachment(
    sender="kprashant49@gmail.com",
    recipient="kprashant49@gmail.com",
    subject="Test Email with Excel Attachment",
    body="Hi, please find the attached Excel file.",
    file_path=r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Headers.xlsx",
    app_password="xiwz fznl vgfj ueky"
)
