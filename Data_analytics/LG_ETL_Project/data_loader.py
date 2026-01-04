import pyodbc
import pandas as pd
from secure_config import load_secure_config


def load_data():
    config = load_secure_config()
    db = config["database"]

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

    # Query C – Audit / Extra report (ATTACHMENT)
    query_c = """
        Select * from ApplicantGender       
    """

    df_a = pd.read_sql(query_a, conn)
    df_b = pd.read_sql(query_b, conn)
    df_c = pd.read_sql(query_c, conn)

    conn.close()

    return df_a, df_b, df_c
