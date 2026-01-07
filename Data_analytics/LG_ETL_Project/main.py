from data_loader import load_data
from analytics import *
from emailer import send_outlook_mail
from secure_config import load_secure_config
import logging
import tempfile
import os
from datetime import datetime, timedelta

def df_to_html(df, empty_message):
    """
    Convert DataFrame to HTML table or show empty message
    """
    if df.empty:
        return f"<p><i>{empty_message}</i></p>"
    return df.to_html(index=False, border=1, justify="left")


def main():
    logging.info("Report mailer started")
    report_date = (datetime.today() - timedelta(days=1)).strftime("%d/%m/%Y")
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")
    to_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        df_a, df_b, df_c, df_d = load_data(from_date, to_date)

        df_a = transform_df_a(df_a)
        df_b = transform_df_b(df_b)
        df_c = transform_df_c(df_c)
        df_d = transform_df_d(df_d)

        a_html = df_to_html(df_a,"No data available for the selected period.")
        b_html = df_to_html(df_b,"No data available for the selected period.")
        d_html = df_to_html(df_d, "No data available for the selected period.")

        html = f"""
        <p>Dear All,</p>
        <p>Please find herewith Data Analytics Report for {report_date}.</p>
        <html>
        <body style="font-family:Arial;">
        <h4>Counts of cases</h4>
        {a_html}
        <h4>Most Rules Triggered</h4>
        {b_html}
        <h4>Most Documents Submitted</h4>
        {d_html}
        </body>
        </html>
        <p>Regards,<br>Loanguard Team</p>
        <p>Please Note. This is an automated email, please do not reply to this email.<p>
        """

        # Create Excel attachment
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_file.close()
        df_c.to_excel(temp_file.name, index=False)

        config = load_secure_config()
        outlook = config["outlook"]

        subject = f"{outlook['subject']} - {report_date}"

        send_outlook_mail(
            subject,
            html,
            outlook,
            attachments=[("Data.xlsx", temp_file.name)]
        )

        os.unlink(temp_file.name)
        logging.info("Report mailer completed successfully.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
