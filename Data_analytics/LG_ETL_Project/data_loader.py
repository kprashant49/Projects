import pyodbc
import pandas as pd
from secure_config import load_secure_config


def load_data(from_date, to_date):
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

    # =========================
    # QUERY A
    # =========================
    query_a = f"""
    SELECT Remarks AS [Type of Case], COUNT(*) AS [Counts]
    FROM (
        SELECT CASE
            WHEN AL_Column = 'Application Create Status' AND AL_Old_Val = 0 AND AL_New_Val = 1 THEN 'New_Case'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val = 'Pending' AND AL_New_Val IN ('Sampled','Screened') THEN 'Processed by LG'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val IN ('Sampled','Screened') AND AL_New_Val = 'Pending' THEN 'Reopen_Case'
        END AS Remarks
        FROM ApplicationAuditLog
        WHERE AL_ClientId = 35
          AND AL_Datetime BETWEEN '{from_date}' AND '{to_date}'

        UNION ALL

        SELECT CASE
            WHEN AL_Column = 'Application Create Status' AND AL_Old_Val = 0 AND AL_New_Val = 1 THEN 'New_Case'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val = 'Pending' AND AL_New_Val IN ('Sampled','Screened') THEN 'Processed by LG'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val IN ('Sampled','Screened') AND AL_New_Val = 'Pending' THEN 'Reopen_Case'
        END
        FROM DBLoanguardHistory.dbo.ApplicationAuditLog
        WHERE AL_ClientId = 35
          AND AL_Datetime BETWEEN '{from_date}' AND '{to_date}'
    ) A
    WHERE Remarks IS NOT NULL
    GROUP BY Remarks
    """

    # =========================
    # QUERY B
    # =========================
    query_b = f"""
    SELECT TOP 10 [Trigger], COUNT(*) AS Counts
    FROM (
        SELECT rm2.Message AS [Trigger]
        FROM DocumentRuleMessages drm
        JOIN DocumentValidatingMessages dvm ON drm.DocValMessageId = dvm.DocValMessageId
        JOIN Applications apn ON dvm.ApplicationId = apn.ApplicationId
        JOIN RuleMaster rm1 ON drm.RuleId = rm1.RuleId
        JOIN RuleMessage rm2 ON drm.RuleId = rm2.RuleId
        WHERE apn.AppStatus IN (1,3)
          AND apn.ClientId = 35
          AND CONVERT(date, apn.ModifiedOn) BETWEEN '{from_date}' AND '{to_date}'

        UNION ALL

        SELECT drm.ManualTrigger
        FROM DocumentManualTrigger drm
        JOIN DocumentValidatingMessages dvm ON drm.DocValMessageId = dvm.DocValMessageId
        JOIN Applications apn ON dvm.ApplicationId = apn.ApplicationId
        WHERE apn.AppStatus IN (1,3)
          AND apn.ClientId = 35
          AND CONVERT(date, apn.ModifiedOn) BETWEEN '{from_date}' AND '{to_date}'
    ) A
    GROUP BY [Trigger]
    ORDER BY Counts DESC
    """

    # =========================
    # QUERY C (ATTACHMENT)
    # =========================
    query_c = f"""
    SELECT dvm.ApplicationNo, dvm.LoanguardId,
           rdd.DocumentName + '-' + CONVERT(varchar(10), dvm.DocumentIndex) AS Document,
           rm2.Message AS [Trigger],
           CASE WHEN rm1.IsHighRiskRule = 1 THEN 'High' ELSE 'Low' END AS [Trigger Severity],
           rss.RuleStatus,
           apn.ModifiedOn,
           aps.StatusDescription
    FROM DocumentRuleMessages drm
    JOIN DocumentValidatingMessages dvm ON drm.DocValMessageId = dvm.DocValMessageId
    JOIN Applications apn ON dvm.ApplicationId = apn.ApplicationId
    JOIN RuleMaster rm1 ON drm.RuleId = rm1.RuleId
    JOIN RuleMessage rm2 ON drm.RuleId = rm2.RuleId
    JOIN RuleStatus rss ON drm.RuleStatus = rss.RuleStatusId
    JOIN ReferenceDocuments rdd ON dvm.DocumentId = rdd.DocumentId
    JOIN ApplicationStatus aps ON apn.AppStatus = aps.StatusId
    WHERE apn.AppStatus IN (1,3)
      AND apn.ClientId = 35
      AND CONVERT(date, apn.ModifiedOn) BETWEEN '{from_date}' AND '{to_date}'
    """

    # =========================
    # QUERY D
    # =========================
    query_d = f"""
    SELECT TOP 20 RD.DocumentDescription, COUNT(*) AS Counts
    FROM DocumentValidatingMessages DVM
    JOIN Applications APN ON DVM.ApplicationNo = APN.ApplicationNo
    JOIN ReferenceDocuments RD ON DVM.DocumentId = RD.DocumentId
    WHERE APN.ClientId = 35
      AND CONVERT(date, DVM.CreatedOn) BETWEEN '{from_date}' AND '{to_date}'
    GROUP BY RD.DocumentDescription
    ORDER BY Counts DESC
    """

    df_a = pd.read_sql(query_a, conn)
    df_b = pd.read_sql(query_b, conn)
    df_c = pd.read_sql(query_c, conn)
    df_d = pd.read_sql(query_d, conn)

    conn.close()
    return df_a, df_b, df_c, df_d