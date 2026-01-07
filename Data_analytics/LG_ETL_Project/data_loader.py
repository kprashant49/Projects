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
        Select Remarks as "Type of Case", count(Remarks) as "Counts" from (Select *,
        case when AL_Column = 'Application Create Status' and AL_Old_Val = 0 and AL_New_Val = 1 then 'New_Case'
        when AL_Column = 'Application Status' and AL_Old_Val = 'Pending' and AL_New_Val = 'Sampled' then 'Processed by LG'
        when AL_Column = 'Application Status' and AL_Old_Val = 'Pending' and (AL_New_Val = 'Sampled' or AL_New_Val = 'Screened') then 'Processed by LG'
        when AL_Column = 'Application Status' and (AL_Old_Val = 'Sampled' or AL_Old_Val = 'Screened') and AL_New_Val = 'Pending' then 'Reopen_Case'
        end AS [Remarks]
        from (Select * from ApplicationAuditLog where 
        AL_ClientId = '35'
        and Year(AL_Datetime) = 2025
        and Month(AL_Datetime) = 12
        and Day(Al_Datetime) between 1 and 31
        union all
        Select * from DBLoanguardHistory.dbo.ApplicationAuditLog where 
        AL_ClientId = '35'
        and Year(AL_Datetime) = 2025
        and Month(AL_Datetime) = 12
        and Day(Al_Datetime) between 1 and 31) A) B where Remarks is not null group by Remarks
        """

    # Query B – Table 2 (NOT related to Query A)
    query_b = """
        Select * from ApplicantGender
    """

    # Query C – Audit / Extra report (ATTACHMENT)
    query_c = """
        Select Remarks as "Type of Case", count(Remarks) as "Counts" from (Select *,
        case when AL_Column = 'Application Create Status' and AL_Old_Val = 0 and AL_New_Val = 1 then 'New_Case'
        when AL_Column = 'Application Status' and AL_Old_Val = 'Pending' and AL_New_Val = 'Sampled' then 'Processed by LG'
        when AL_Column = 'Application Status' and AL_Old_Val = 'Pending' and (AL_New_Val = 'Sampled' or AL_New_Val = 'Screened') then 'Processed by LG'
        when AL_Column = 'Application Status' and (AL_Old_Val = 'Sampled' or AL_Old_Val = 'Screened') and AL_New_Val = 'Pending' then 'Reopen_Case'
        end AS [Remarks]
        from (Select * from ApplicationAuditLog where 
        AL_ClientId = '35'
        and Year(AL_Datetime) = 2025
        and Month(AL_Datetime) = 12
        and Day(Al_Datetime) between 1 and 31
        union all
        Select * from DBLoanguardHistory.dbo.ApplicationAuditLog where 
        AL_ClientId = '35'
        and Year(AL_Datetime) = 2025
        and Month(AL_Datetime) = 12
        and Day(Al_Datetime) between 1 and 31) A) B where Remarks is not null group by Remarks     
        """

    df_a = pd.read_sql(query_a, conn)
    df_b = pd.read_sql(query_b, conn)
    df_c = pd.read_sql(query_c, conn)

    conn.close()

    return df_a, df_b, df_c
