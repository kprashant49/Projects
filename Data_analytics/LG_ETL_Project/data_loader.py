import pyodbc
import pandas as pd
from secure_config import load_secure_config


def load_data(client_id, from_date, to_date):
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
            WHEN AL_Column = 'Application Create Status' AND AL_Old_Val = 0 AND AL_New_Val = 1 THEN 'Fresh Cases Submitted'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val = 'Pending' AND AL_New_Val IN ('Sampled','Screened') THEN 'Cases Processed by LG'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val IN ('Sampled','Screened') AND AL_New_Val = 'Pending' THEN 'Reopened Cases'
        END AS Remarks
        FROM ApplicationAuditLog
        WHERE AL_ClientId = {client_id}
          AND AL_Datetime BETWEEN '{from_date}' AND '{to_date}'

        UNION ALL

        SELECT CASE
            WHEN AL_Column = 'Application Create Status' AND AL_Old_Val = 0 AND AL_New_Val = 1 THEN 'Fresh Cases Submitted'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val = 'Pending' AND AL_New_Val IN ('Sampled','Screened') THEN 'Cases Processed by LG'
            WHEN AL_Column = 'Application Status' AND AL_Old_Val IN ('Sampled','Screened') AND AL_New_Val = 'Pending' THEN 'Reopened Cases'
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
    # query_b = f"""
    # SELECT TOP 10 [Trigger], COUNT(*) AS Counts
    # FROM (
    #     SELECT rm2.Message AS [Trigger]
    #     FROM DocumentRuleMessages drm
    #     JOIN DocumentValidatingMessages dvm ON drm.DocValMessageId = dvm.DocValMessageId
    #     JOIN Applications apn ON dvm.ApplicationId = apn.ApplicationId
    #     JOIN RuleMaster rm1 ON drm.RuleId = rm1.RuleId
    #     JOIN RuleMessage rm2 ON drm.RuleId = rm2.RuleId
    #     WHERE apn.AppStatus IN (1,3)
    #       AND apn.ClientId = {client_id}
    #       AND CONVERT(date, apn.ModifiedOn) BETWEEN '{from_date}' AND '{to_date}'
    #
    #     UNION ALL
    #
    #     SELECT drm.ManualTrigger
    #     FROM DocumentManualTrigger drm
    #     JOIN DocumentValidatingMessages dvm ON drm.DocValMessageId = dvm.DocValMessageId
    #     JOIN Applications apn ON dvm.ApplicationId = apn.ApplicationId
    #     WHERE apn.AppStatus IN (1,3)
    #       AND apn.ClientId = {client_id}
    #       AND CONVERT(date, apn.ModifiedOn) BETWEEN '{from_date}' AND '{to_date}'
    # ) A
    # GROUP BY [Trigger]
    # ORDER BY Counts DESC
    # """

    # =========================
    # QUERY C
    # =========================
    query_c = f"""
    Select A.DocumentDescription [Document Name], B.Document_Count [Counts] from ReferenceDocuments A 
    join (Select DISTINCT  DocumentID,  Count(DocumentId) OVER (PARTITION BY (DocumentID) order by DocumentID) as 'Document_Count' from DocumentValidatingMessages DVM 
    join Applications APN on DVM.ApplicationNo = APN.ApplicationNo
    where ClientId = {client_id}
    AND CONVERT(date, DVM.CreatedOn) BETWEEN '{from_date}' AND '{to_date}') B
    on A.DocumentID = B.DocumentID
    and A.DocType in ('A','I','K')
    order by Document_Count desc
    """

    # =========================
    # QUERY D
    # =========================
    query_d = f"""
    Select [Delete Reason], count([Delete Reason]) [Counts] from (select a.ApplicationNo as CaseID,
    case when a.CreateMode='W' then 'API' else 'SFTP' end as 'Case Mode',
    am.ApplicantName as 'Applicant Name',
    apt.TypeDescription 'Applicant Type',
    CreatedOn as 'Case Initiated Date',
    CreateStatusOn as 'Mark Complete Date',
    ModifiedOn as 'Reported Date',
    aps.StatusDescription as Status,
    rd.DocumentName+'-'+convert(varchar(10),ddd.DocumentIndex) as 'Delete Document',
    ddr.DeleteReason as 'Delete Reason',
    ddd.DeletedOn as 'Delete DateTime',
    tumm.UserDetails as 'User Name'
    from Applications a 
    join ApplicantMaster am on a.ApplicationId=am.ApplicationId
    join ApplicantType apt on am.TypeId=apt.TypeId
    join DeletedDocumentDetails ddd on am.LoanguardId=ddd.LoanguardId
    join ReferenceDocuments rd on ddd.DocumentId=rd.DocumentId
    join DocDeletedReasons ddr on ddd.DeleteRemark=ddr.Rid
    join ApplicationStatus aps on a.AppStatus=aps.StatusId
    join tblUserMst tumm on ddd.UserId=tumm.UserID
    where a.ClientId = {client_id}
    AND CONVERT(date, A.CreatedOn) BETWEEN '{from_date}' AND '{to_date}') A group by [Delete Reason] order by 2 Desc
    """

    df_a = pd.read_sql(query_a, conn)
    # df_b = pd.read_sql(query_b, conn)
    df_c = pd.read_sql(query_c, conn)
    df_d = pd.read_sql(query_d, conn)
    df_b = pd.read_sql_query("EXEC dbo.GetTATAndMarkTATIsApplicableOrNot_ForTMF @FromDate=?, @ToDate=?, @ClientId=?",
        conn, params=[from_date, to_date, client_id])
    conn.close()
    return df_a, df_b, df_c, df_d