from logger import setup_logging
from data_loader import load_data
from analytics import transform_df_a, transform_df_b
from emailer import send_email
import logging


def df_to_html(df, empty_message):
    """
    Convert DataFrame to HTML table or show empty message
    """
    if df.empty:
        return f"<p><i>{empty_message}</i></p>"

    return df.to_html(index=False, border=1)


def main():
    setup_logging()
    logging.info("Report mailer started")

    try:
        df_a, df_b = load_data()

        df_a = transform_df_a(df_a)
        df_b = transform_df_b(df_b)

        a_html = df_to_html(
            df_a,
            "No sales data available for the selected period."
        )

        b_html = df_to_html(
            df_b,
            "No customer data available."
        )

        html = f"""
        <p>Dear All,</p>
        <p>Enclosed please find herewith eRCU status along with screening and sampling reports for 30/12/2025</p>
        <html>
        <body style="font-family:Arial;">
            <h3>Report A</h3>
            {a_html}
            <br><br>
            <h3>Report B</h3>
            {b_html}
        </body>
        </html>
        <p>Regards,<br>Loanguard Team</p>
        <p>Please Note. This is an automated email, please do not reply to this email.<p>
        """

        send_email(html)
        logging.info("Report mailer completed successfully")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
