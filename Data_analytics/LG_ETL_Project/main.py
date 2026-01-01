from data_loader import load_data
from analytics import transform_df_a, transform_df_b, transform_df_c
from emailer import send_outlook_mail, load_outlook_config
import logging
import tempfile
import os


def df_to_html(df, empty_message):
    """
    Convert DataFrame to HTML table or show empty message
    """
    if df.empty:
        return f"<p><i>{empty_message}</i></p>"
    return df.to_html(index=False, border=1)


def main():
    logging.info("Report mailer started")

    try:
        df_a, df_b, df_c = load_data()

        df_a = transform_df_a(df_a)
        df_b = transform_df_b(df_b)
        df_c = transform_df_c(df_c)

        a_html = df_to_html(df_a,"No sales data available for the selected period.")
        b_html = df_to_html(df_b,"No customer data available.")

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

        # Create Excel attachment
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_file.close()
        df_c.to_excel(temp_file.name, index=False)

        outlook = load_outlook_config()
        send_outlook_mail(
            outlook["subject"],
            html,
            outlook,
            attachments=[("c_report.xlsx", temp_file.name)]
        )
        os.unlink(temp_file.name)
        logging.info("Report mailer completed successfully.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
