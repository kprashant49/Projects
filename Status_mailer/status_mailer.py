import pandas as pd
import logging
import configparser
from Snowflake_connection import get_snowflake_connection, load_config

query = """
SELECT 'ICICI' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_ICICI

UNION ALL

SELECT 'CITI' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_CITI

UNION ALL

SELECT 'HDFC' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_HDFC

UNION ALL

SELECT 'Saraswa' AS "Bank Name",
       MAX(TO_DATE(lot_dt, 'DD-MON-YY')) AS "Max Transaction Date"
FROM GROUP_SHARE_INDIA.FINANCE.MARTS_CASH_FLOW_SARAS
"""

def setup_logging():
    logging.basicConfig(
        filename='status_mailer.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def query_to_df(query, config):
    conn = get_snowflake_connection(config)
    try:
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

def status_mailer():
    setup_logging()
    logging.info("Starting Status Mailer (Snowflake mode)")

    try:
        config = load_config('config.ini')
        df = query_to_df(query, config)
        logging.info("etched latest transaction dates successfully.")
        print(df)

    except Exception as e:
        logging.error(f"Error while fetching data: {e}")
        raise

if __name__ == "__main__":
    status_mailer()
