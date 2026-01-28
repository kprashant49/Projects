from data_loader import load_data
from analytics import *
from emailer import send_outlook_mail, send_failure_alert
from secure_config import load_secure_config
import logging
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
            df_a, df_b, df_c, df_d, df_e = load_data(
                client_id=client_id,
                from_date=from_date,
                to_date=to_date
            )

            # -------- Transformations --------
            df_a = transform_df_a(df_a)
            df_raw = df_b.copy()
            df_b = transform_df_b(df_raw)
            df_b_1 = transform_df_b_1(df_raw)
            df_b_2 = transform_df_b_2(df_raw)
            df_c = transform_df_c(df_c)
            df_d = transform_df_d(df_d)
            df_e = transform_df_e(df_e)

            # -------- Export the dfs --------
            export_dataframes_to_excel(
                {
                    "Report_A": df_a,
                    "Report_B": df_b,
                    "Report_B_1": df_b_1,
                    "Report_B_2": df_b_2,
                    "Report_C": df_c,
                    "Report_D": df_d,
                    "Report_E": df_e
                },
                client_name=client_name
            )

            # -------- HTML tables --------
            a_html = df_to_html(df_a, "No data available for the selected period.")
            b_html = df_to_html(df_b, "No data available for the selected period.")
            b_1_html = df_to_html(df_b_1, "No data available for the selected period.")
            b_2_html = df_to_html(df_b_2, "No data available for the selected period.")
            c_html = df_to_html(df_c, "No data available for the selected period.")
            d_html = df_to_html(df_d, "No data available for the selected period.")

            # -------- Email body --------
            html = f"""
            <html>
            <body style="font-family:Arial, Helvetica, sans-serif; font-size:13px; margin:0; padding:0;">

            <p style="margin:8px 0;">Dear Team,</p>

            <p style="margin:8px 0;">
            Please find below the <b>{client_name}</b> Data Analytics Report for <b>{report_date}</b>.
            </p>

            <p style="margin:8px 0;font-weight:bold;">Cases Submitted and Processed by Loanguard</p>
            {a_html}

            <p style="margin:12px 0;font-weight:bold;">Distribution of Day-wise Cases received by Loanguard</p>
            {b_2_html}

            <p style="margin:12px 0;font-weight:bold;">Sampling and TAT Summary</p>
            {b_html}

            <p style="margin:12px 0;font-weight:bold;">Working Hours vs Process Summary</p>
            {b_1_html}

            <p style="margin:12px 0;font-weight:bold;">Most Documents Submitted</p>
            {c_html}

            <p style="margin:12px 0;font-weight:bold;">Most Documents Deleted</p>
            {d_html}

            <p style="margin:8px 0;">
            Regards,<br>
            <b>Loanguard Team</b>
            </p>

            <p style="margin:6px 0;font-size:11px;color:#666;">
            <i>This is an automated email. Please do not reply.</i>
            </p>

            </body>
            </html>
            """

            # -------- Excel attachment (Single df) --------
            raw_export_path = export_single_dataframe_to_excel(
                df_raw,
                client_name=client_name
            )

            subject = f"{client_name} - {outlook['subject']} - {report_date}"

            send_outlook_mail(
                subject,
                html,
                outlook,
                attachments=[(os.path.basename(raw_export_path), raw_export_path)]
            )

            # -------- Excel attachment (Multiple dfs)--------
            # exported_file_path = export_dataframes_to_excel(
            #     {
            #         "Report_A": df_a,
            #         "Report_B": df_b,
            #         "Report_C": df_c,
            #         "Report_D": df_d
            #     },
            #     client_name=client_name
            # )
            #
            # subject = f"{client_name} - {outlook['subject']} - {report_date}"
            #
            # send_outlook_mail(
            #     subject,
            #     html,
            #     outlook,
            #     attachments=[(os.path.basename(exported_file_path), exported_file_path)]
            # )

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