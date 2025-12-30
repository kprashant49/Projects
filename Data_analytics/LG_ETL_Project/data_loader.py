import pyodbc
import pandas as pd
import json


def load_data():
    with open("config.json") as f:
        db = json.load(f)["database"]

    conn_str = (
        f"DRIVER={{{db['driver']}}};"
        f"SERVER={db['server']};"
        f"DATABASE={db['database']};"
        f"UID={db['username']};"
        f"PWD={db['password']};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    conn = pyodbc.connect(conn_str)

    # Query A – Table 1
    query_a = """
        Select * from ApplicantType
    """

    # Query B – Table 2 (NOT related to Query A)
    query_b = """
        Select * from ApplicantGender
    """

    df_a = pd.read_sql(query_a, conn)
    df_b = pd.read_sql(query_b, conn)

    conn.close()

    return df_a, df_b
