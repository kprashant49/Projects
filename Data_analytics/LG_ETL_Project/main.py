from logger import setup_logging
from data_loader import load_data
from analytics import transform_sales, transform_customers
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
        df_sales, df_customers = load_data()

        df_sales = transform_sales(df_sales)
        df_customers = transform_customers(df_customers)

        sales_html = df_to_html(
            df_sales,
            "No sales data available for the selected period."
        )

        customers_html = df_to_html(
            df_customers,
            "No customer data available."
        )

        html = f"""
        <html>
        <body style="font-family:Arial;">
            <h3>Sales Report</h3>
            {sales_html}
            <br><br>
            <h3>Customer Report</h3>
            {customers_html}
        </body>
        </html>
        """

        send_email(html)
        logging.info("Report mailer completed successfully")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
