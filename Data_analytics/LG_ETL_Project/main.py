from data_loader import load_data
from analytics import *
from emailer import send_outlook_mail, send_failure_alert
from secure_config import load_secure_config
import logging
import tempfile
import os
from datetime import datetime, timedelta
from analytics import export_dataframes_to_excel

def df_to_html(df, empty_message):
    """
    Convert DataFrame to HTML table or show empty message
    """
    if df.empty:
        return f"<p><i>{empty_message}</i></p>"
    return df.to_html(index=False, border=1, justify="left")


def main():
    logging.info("Report mailer started")

    # -------------------------
    # Date calculations
    # -------------------------
    report_date = (datetime.today() - timedelta(days=1)).strftime("%d/%m/%Y")
    today = datetime.today()
    from_date = today.replace(day=1).strftime("%Y-%m-%d")
    to_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # -------------------------
    # Load full configuration
    # -------------------------
    config = load_secure_config()
    clients = config["clients"]

    # -------------------------
    # Process EACH client independently
    # -------------------------
    for client in clients:
        client_id = client["client_id"]
        outlook = client["outlook"]
        client_name = client.get("client_name", f"Client {client_id}")

        logging.info(f"Processing client: {client_name} ({client_id})")

        try:
            # -------- Data load --------
            df_a, df_b, df_c, df_d = load_data(
                client_id=client_id,
                from_date=from_date,
                to_date=to_date
            )

            # -------- Transformations --------
            df_a = transform_df_a(df_a)
            df_b = transform_df_b(df_b)
            df_c = transform_df_c(df_c)
            df_d = transform_df_d(df_d)

            # -------- Export the dfs --------
            export_dataframes_to_excel({
                "Report_A": df_a,
                "Report_B": df_b,
                "Report_C": df_c,
                "Report_D": df_d
            })

            # -------- HTML tables --------
            a_html = df_to_html(df_a, "No data available for the selected period.")
            b_html = df_to_html(df_b, "No data available for the selected period.")
            d_html = df_to_html(df_d, "No data available for the selected period.")

            # -------- Email body --------
            html = f"""
            <html>
            <body style="font-family:Arial;">
                <p>Dear Team,</p>
                <p>Please find herewith <b>{client_name}</b> Data Analytics Report for {report_date}.</p>

                <h4>Counts of cases</h4>
                {a_html}

                <h4>Most Rules Triggered</h4>
                {b_html}

                <h4>Most Documents Submitted</h4>
                {d_html}

                <p>Regards,<br>Loanguard Team</p>
                <p><i>This is an automated email. Please do not reply.</i></p>
            </body>
            </html>
            """

            # -------- Excel attachment --------
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            temp_file.close()
            df_c.to_excel(temp_file.name, index=False)

            subject = f"{client_name} - {outlook['subject']} - {report_date}"

            send_outlook_mail(
                subject,
                html,
                outlook,
                attachments=[("Data.xlsx", temp_file.name)]
            )

            os.unlink(temp_file.name)

            logging.info(f"Completed client successfully: {client_name} ({client_id})")

        except Exception as e:
            # -------- Client-level failure handling --------
            logging.error(f"Client failed: {client_name} ({client_id})")
            logging.error(str(e))

            send_failure_alert(
                subject=f"{client_name} - Daily Analytics Job",
                error_message=str(e)
            )

            # IMPORTANT: continue to next client
            continue

    logging.info("Report mailer finished for all clients")

if __name__ == "__main__":
    main()