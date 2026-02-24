SELECT *
FROM
(
    select 
        mmm.ApplicationNo AS CaseId,
        mmm.LoanguardId AS LgId,
        apn.CreateStatusOn AS MarkCompleteDateTime,
        apn.ModifiedOn AS ReportDateTime,
        aps.StatusDescription AS CaseStatus,
        mmm.URLMapName AS APIName,
        mmm.RequestParameters AS APIRequest,
        mmm.Response AS APIResponse
    from MerchantURLLogDetails MMM
    join Applications APN on MMM.ApplicationNo = APN.ApplicationNo
    join ApplicationStatus aps on APN.AppStatus = aps.StatusId
    join LoanProductMaster lpm on APN.ProductId = lpm.ProductId 
    where APN.ClientId = 35 
      and APN.AppStatus in (1,3,5)
      and year(APN.ModifiedOn) = 2026
      and month(APN.ModifiedOn) = 02
      and DAY(APN.ModifiedOn) BETWEEN 01 AND 15

    UNION ALL
 
    select 
        mmm.ApplicationNo AS CaseId,
        mmm.LoanguardId AS LgId,
        apn.CreateStatusOn AS MarkCompleteDateTime,
        apn.ModifiedOn AS ReportDateTime,
        aps.StatusDescription AS CaseStatus,
        mmm.URLMapName AS APIName,
        mmm.RequestParameters AS APIRequest,
        mmm.Response AS APIResponse
    from DBLoanguardHistory.dbo.MerchantURLLogDetails MMM
    join Applications APN on MMM.ApplicationNo = APN.ApplicationNo
    join ApplicationStatus aps on APN.AppStatus = aps.StatusId
    join LoanProductMaster lpm on APN.ProductId = lpm.ProductId 
    where APN.ClientId = 35 
      and APN.AppStatus in (1,3,5)
      and year(APN.ModifiedOn) = 2026
      and month(APN.ModifiedOn) = 02
      and DAY(APN.ModifiedOn) BETWEEN 01 AND 15
) t
ORDER BY t.ReportDateTime;