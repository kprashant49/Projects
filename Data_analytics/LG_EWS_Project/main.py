from data_loader import load_data
from emailer import send_outlook_mail
from secure_config import load_secure_config
import logging
import pandas as pd


def main():
    logging.info("EWS mailer started")

    # -------- Load config --------
    config = load_secure_config()
    recipient = config["recipients"][0]
    outlook = recipient["outlook"]
    subject = outlook["subject"]

    # -------- Load data --------
    df_a, df_b, df_c = load_data()

    # Merge summary + lens sync count
    df_a_new = pd.concat([df_a, df_b], axis=1)

    # -------- Breach logic --------
    THRESHOLD = 100

    apps_breach = (df_a_new[["Pending_Apps_OCR", "Pending_Apps_Rule", "Pending_Apps_Callback"]] >= THRESHOLD).any().any()

    lens_sync_breach = df_b["Pending_Lens<>Lg_Sync"].iloc[0] > 1

    if not (apps_breach or lens_sync_breach):
        logging.info("No breach. Mail not sent.")
        return

    # -------- HTML: main summary --------
    a_html = (
        df_a_new.to_html(index=False, escape=False, border=1)
        if not df_a_new.empty
        else "<p><i>No data available.</i></p>"
    )

    # -------- HTML: Lens sync details (conditional) --------
    b_html = ""
    if lens_sync_breach and not df_c.empty:
        b_html = """
        <p style="margin:12px 0; font-weight:bold;">
            Please check below cases that are pending to be pushed to Lens.
        </p>
        """
        b_html += df_c.to_html(index=False, escape=False, border=1)

    # -------- Email body --------
    html = f"""
    <html>
    <body style="font-family:Arial, Helvetica, sans-serif; font-size:13px;">

        <p>Dear Team,</p>

        <p>Please check the services' status below.</p>

        {a_html}

        {b_html}

        <p>
            Regards,<br>
            <b>Loanguard Team</b>
        </p>

    </body>
    </html>
    """

    send_outlook_mail(subject, html, outlook)
    logging.info("EWS mailer finished")


if __name__ == "__main__":
    main()