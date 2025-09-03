from mailer import setup_logging, load_outlook_config, run_query, send_mail, load_config

query = """ -- your cleaned SQL here -- """

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

    send_mail(subject, body_html, outlook_config)

if __name__ == "__main__":
    main()
