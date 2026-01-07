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
        Select Top 10 [Trigger], Count([Trigger]) as Counts from (select dvm.ApplicationNo [Case Id],dvm.LoanguardId [Lg Id],
        rdd.DocumentName+'-'+convert(varchar(10),dvm.DocumentIndex) [Document],
        rm2.Message [Trigger],
        case when rm1.IsHighRiskRule=1 then 'High' else 'Low' end as [Trigger Severity],
        rss.RuleStatus [Trigger Status],
        apn.ModifiedOn [Report Date],aps.StatusDescription [Case Status]
        from DocumentRuleMessages drm
        join DocumentValidatingMessages dvm on drm.DocValMessageId=dvm.DocValMessageId
        join Applications apn on dvm.ApplicationId=apn.ApplicationId
        join RuleMaster rm1 on drm.RuleId=rm1.RuleId
        join RuleMessage rm2 on drm.RuleId=rm2.RuleId
        join RuleStatus rss on drm.RuleStatus=rss.RuleStatusId
        join ReferenceDocuments rdd on dvm.DocumentId=rdd.DocumentId
        join ApplicationStatus aps on apn.AppStatus=aps.StatusId
        where apn.AppStatus in (1,3) and apn.ClientId=35
        and CONVERT(DATE,apn.ModifiedOn,103)>=CONVERT(DATE,'01/12/2025',103)
        and CONVERT(DATE,apn.ModifiedOn,103)<=CONVERT(DATE,'31/12/2025',103)
        
        union all
        
        select dvm.ApplicationNo [Case Id],dvm.LoanguardId [Lg Id],
        rdd.DocumentName+'-'+convert(varchar(10),dvm.DocumentIndex) [Document],
        drm.ManualTrigger [Trigger],
        drm.Severity [Trigger Severity],
        '' as [Trigger Status],
        apn.ModifiedOn [Report Date],aps.StatusDescription [Case Status]
        from DocumentManualTrigger drm
        join DocumentValidatingMessages dvm on drm.DocValMessageId=dvm.DocValMessageId
        join Applications apn on dvm.ApplicationId=apn.ApplicationId
        join ReferenceDocuments rdd on dvm.DocumentId=rdd.DocumentId
        join ApplicationStatus aps on apn.AppStatus=aps.StatusId
        where apn.AppStatus in (1,3) and apn.ClientId=35
        and CONVERT(DATE,apn.ModifiedOn,103)>=CONVERT(DATE,'01/12/2025',103)
        and CONVERT(DATE,apn.ModifiedOn,103)<=CONVERT(DATE,'31/12/2025',103)) A group by [Trigger] order by 2 desc
        """

    # Query C – Audit / Extra report (ATTACHMENT)
    query_c = """
        select dvm.ApplicationNo [Case Id],dvm.LoanguardId [Lg Id],
        rdd.DocumentName+'-'+convert(varchar(10),dvm.DocumentIndex) [Document],
        rm2.Message [Trigger],
        case when rm1.IsHighRiskRule=1 then 'High' else 'Low' end as [Trigger Severity],
        rss.RuleStatus [Trigger Status],
        apn.ModifiedOn [Report Date],aps.StatusDescription [Case Status]
        from DocumentRuleMessages drm
        join DocumentValidatingMessages dvm on drm.DocValMessageId=dvm.DocValMessageId
        join Applications apn on dvm.ApplicationId=apn.ApplicationId
        join RuleMaster rm1 on drm.RuleId=rm1.RuleId
        join RuleMessage rm2 on drm.RuleId=rm2.RuleId
        join RuleStatus rss on drm.RuleStatus=rss.RuleStatusId
        join ReferenceDocuments rdd on dvm.DocumentId=rdd.DocumentId
        join ApplicationStatus aps on apn.AppStatus=aps.StatusId
        where apn.AppStatus in (1,3) and apn.ClientId=35
        and CONVERT(DATE,apn.ModifiedOn,103)>=CONVERT(DATE,'01/12/2025',103)
        and CONVERT(DATE,apn.ModifiedOn,103)<=CONVERT(DATE,'31/12/2025',103)
        
        union all
        
        select dvm.ApplicationNo [Case Id],dvm.LoanguardId [Lg Id],
        rdd.DocumentName+'-'+convert(varchar(10),dvm.DocumentIndex) [Document],
        drm.ManualTrigger [Trigger],
        drm.Severity [Trigger Severity],
        '' as [Trigger Status],
        apn.ModifiedOn [Report Date],aps.StatusDescription [Case Status]
        from DocumentManualTrigger drm
        join DocumentValidatingMessages dvm on drm.DocValMessageId=dvm.DocValMessageId
        join Applications apn on dvm.ApplicationId=apn.ApplicationId
        join ReferenceDocuments rdd on dvm.DocumentId=rdd.DocumentId
        join ApplicationStatus aps on apn.AppStatus=aps.StatusId
        where apn.AppStatus in (1,3) and apn.ClientId=35
        and CONVERT(DATE,apn.ModifiedOn,103)>=CONVERT(DATE,'01/12/2025',103)
        and CONVERT(DATE,apn.ModifiedOn,103)<=CONVERT(DATE,'31/12/2025',103)
        """

    # Query D – Audit / Extra report
    query_d = """
        Select TOP 20 DocumentDescription, count(DocumentDescription) as Counts from (Select DVM.ApplicationNo, DVM.LoanguardId, DVM.DocumentID, RD.DocumentDescription from DocumentValidatingMessages DVM 
        join Applications APN on DVM.ApplicationNo = APN.ApplicationNo
        join ReferenceDocuments RD on DVM.DocumentId = RD.DocumentId
        where ClientId = 35 
        and Year(DVM.CreatedOn) = 2025
        and Month(DVM.CreatedOn) = 12) A group by DocumentDescription order by 2 desc
        """



    df_a = pd.read_sql(query_a, conn)
    df_b = pd.read_sql(query_b, conn)
    df_c = pd.read_sql(query_c, conn)
    df_d = pd.read_sql(query_d, conn)

    conn.close()

    return df_a, df_b, df_c, df_d
