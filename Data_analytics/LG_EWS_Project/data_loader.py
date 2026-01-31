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
    cursor = conn.cursor()
    cursor.execute("EXEC dbo.GetServicePendingAppsCounts")

    # Move to the first result set that has columns
    while cursor.description is None:
        cursor.nextset()

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    df_a = pd.DataFrame.from_records(rows, columns=columns)

    query_b = f"""
    Select count(*) [Pending_Lens<>Lg_Sync] from (SELECT A.ApplicationNo, A.CreatedOn, A.ModifiedOn, A.StatusDescription [LG_Status], B.Status [LENS_Status]
    FROM (SELECT apn.ApplicationNo, aps.StatusDescription, apn.CreatedOn, apn.ModifiedOn FROM dbo.Applications AS apn
    JOIN dbo.ApplicationStatus AS aps ON apn.AppStatus = aps.StatusId
    WHERE apn.CreateStatus = 1
    AND apn.ClientId = 60
    AND apn.CreatedOn >= DATEADD(DAY, -30, GETDATE())
    AND apn.ModifiedOn <= DATEADD(MINUTE, -15, GETDATE())
    AND apn.AppStatus IN (1,3,4,5,7)) AS A
    JOIN DBLgLens.dbo.Application AS B ON A.ApplicationNo = B.ApplicationNo
    WHERE B.Status in ('Pending','String')
    AND A.StatusDescription in ('Screened','Sampled','Rejected')) C
    """

    query_c = f"""
    SELECT A.ApplicationNo, A.CreatedOn, A.ModifiedOn, A.StatusDescription [LG_Status], B.Status [LENS_Status]
    FROM (SELECT apn.ApplicationNo, aps.StatusDescription, apn.CreatedOn, apn.ModifiedOn FROM dbo.Applications AS apn
    JOIN dbo.ApplicationStatus AS aps ON apn.AppStatus = aps.StatusId
    WHERE apn.CreateStatus = 1
    AND apn.ClientId = 60
    AND apn.CreatedOn >= DATEADD(DAY, -30, GETDATE())
    AND apn.ModifiedOn <= DATEADD(MINUTE, -15, GETDATE())
    AND apn.AppStatus IN (1,3,4,5,7)) AS A
    JOIN DBLgLens.dbo.Application AS B ON A.ApplicationNo = B.ApplicationNo
    WHERE B.Status in ('Pending','String')
    AND A.StatusDescription in ('Screened','Sampled','Rejected')
    ORDER BY A.CreatedOn ASC
    """

    df_b = pd.read_sql(query_b, conn)
    df_c = pd.read_sql(query_c, conn)

    conn.close()
    
    return df_a, df_b, df_c