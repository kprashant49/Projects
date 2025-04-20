import snowflake.connector
import pandas as pd

# Snowflake connection parameters
SNOWFLAKE_CONFIG = {
    "user": "KPRASHANT49",
    "password": "KrPapillonA6",
    "account": "CAVKSJX-DS08600",
    "warehouse": "COMPUTE_WH",
    "database": "MYFIRSTPROJECT",
    "schema": "PUBLIC",
    "role": "ACCOUNTADMIN"
}

# Connect to Snowflake
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_CONFIG["user"],
        password=SNOWFLAKE_CONFIG["password"],
        account=SNOWFLAKE_CONFIG["account"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"],
        role=SNOWFLAKE_CONFIG["role"]
    )


# Create a table in Snowflake
def create_table():
    create_table_query = """
    CREATE OR REPLACE TABLE RTO_DATA2 (
	    REGISTRATION_NUMBER VARCHAR(16777216),
	    CITY_UT VARCHAR(16777216),
	    STATE VARCHAR(16777216)
    );
    """

    conn = get_snowflake_connection()
    cur = conn.cursor()
    try:
        cur.execute(create_table_query)
        print("Table created successfully.")
    finally:
        cur.close()
        conn.close()


# Insert values from CSV to Snowflake
def insert_data_from_csv(csv_file):
    df = pd.read_csv(csv_file)

    conn = get_snowflake_connection()
    cur = conn.cursor()

    try:
        for _, row in df.iterrows():
            cur.execute(
                "INSERT INTO RTO_DATA2 (REGISTRATION_NUMBER, CITY_UT, STATE) VALUES (%s, %s, %s)",
                (row['REGISTRATION_NUMBER'], row['CITY_UT'], row['STATE'])
            )
        conn.commit()
        print("Data inserted successfully.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_table()
    insert_data_from_csv("D:\\Projects\\my_new_project\\rto_data.csv")