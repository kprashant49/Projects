from mailer import (
    setup_logging, load_outlook_config, run_query, send_mail, load_config,
    df_to_excel_bytes, df_to_pdf_bytes
)

query = """ -- your cleaned SQL query here -- """

def main():
    setup_logging()
    sf_config = load_config("config.ini")
    outlook_config = load_outlook_config("config.ini")

    df = run_query(query, sf_config)
    df_html = df.to_html(index=False, border=1, justify="center")

    subject = "India Cashbook Latest Transaction Report"
    body_html = f"""
        <p>Dear All,</p>
        <p>Please find below the latest transaction dates for each bank.</p>
        {df_html}
        <p>Regards,<br>D&A Team</p>
    """

    # Attachments based on config
    attachments = []
    if outlook_config["send_excel"]:
        attachments.append({
            "name": "Cashbook_Report.xlsx",
            "content_bytes": df_to_excel_bytes(df),
            "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })
    if outlook_config["send_pdf"]:
        attachments.append({
            "name": "Cashbook_Report.pdf",
            "content_bytes": df_to_pdf_bytes(df),
            "mime": "application/pdf",
        })

    send_mail(subject, body_html, outlook_config, attachments)

if __name__ == "__main__":
    main()
