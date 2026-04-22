import pyodbc
import json
import os
import pandas as pd
import xlsxwriter

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
DB = config["DB"]
OUTPUT_PATH = config["OUTPUT_PATH"]

# Load SQL from external file
with open(config["QUERY_FILE"], "r", encoding="utf-8") as f:
    QUERY = f.read()

# Build connection string
conn_str = (
    f"DRIVER={DB['DRIVER']};"
    f"SERVER={DB['SERVER']};"
    f"DATABASE={DB['DATABASE']};"
    f"UID={DB['USER']};"
    f"PWD={DB['PASSWORD']};"
    f"Encrypt={DB['ENCRYPT']};"
    f"TrustServerCertificate={DB['TRUSTSERVERCERTIFICATE']};"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute(QUERY)

# Get column names dynamically from query
columns = [col[0] for col in cursor.description]

final_data = []

for row in cursor.fetchall():
    row_dict = dict(zip(columns, row))
    final_data.append(row_dict)

# Ensure directory exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Save JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, default=str)

print(f"JSON saved at: {OUTPUT_PATH}")

cursor.close()
conn.close()

JSON_PATH = r"C:\Users\kpras\Desktop\Output.json"

API_MAPPING = {
    "PanProAPI": {
        "RequestKey": "PanProData",
        "ResponseKey": "panProDTO"
    },
    "BankAPI": {
        "RequestKey": "Bankdata",
        "ResponseKey": "bankDTO"
    },
    "GSTAPI": {
        "RequestKey": "GSTData",
        "ResponseKey": "gSTDTO"
    },
    "DrivingLicenceAPI": {
        "RequestKey": "DLdata",
        "ResponseKey": "drivingLicenseDTO"
    },
    "PanAPI": {
        "RequestKey": "Pandata",
        "ResponseKey": "panCardDTO"
    },
    "ElectricityBillAPI": {
        "RequestKey": "MSEBdata",
        "ResponseKey": "electricityBillDTO"
    },
    "VehicleRCAPI": {
        "RequestKey": "RCData",
        "ResponseKey": "vehicleRCDTO"
    },
    "VoterIdAPI": {
        "RequestKey": "VoterData",
        "ResponseKey": "voterCardDTO"
    },
    "EmploymentCheckAPIInternal": {
        "RequestKey": "EmploymentCheckData",
        "ResponseKey": "employmentCheckDTO"
    },
    "AadharAPI": {
        "RequestKey": "AadharData",
        "ResponseKey": "aadharCardDTO"
    },
    "CAMembershipVerificationAPI": {
        "RequestKey": "CAMembershipVerificationData",
        "ResponseKey": "caMembershipDTO"
    },
    "UdyamAadharAPI": {
        "RequestKey": "UdyamAadharData",
        "ResponseKey": "udyamAadharDTO"
    },
    "ShopActAPI": {
        "RequestKey": "ShopActData",
        "ResponseKey": "shopActDTO"
    },
    "EmploymentCheckWithMobileNumberAPI": {
        "RequestKey": "EmpCheckWithMobileNumData",
        "ResponseKey": "empCheckWithMobileNumberDTO"
    },
    "MobileLookupAPI": {
        "RequestKey": "MobileLookupData",
        "ResponseKey": "mobileLookupDTO"
    },
    "VehicleRCAdvanceAPI": {
        "RequestKey": "RCAdvanceData",
        "ResponseKey": "vehicleRCAdvanceDTO"
    },
}

df = pd.read_json(JSON_PATH)

# PARSE JSON STRINGS
df["APIRequest_dict"] = df["APIRequest"].apply(lambda x: json.loads(x) if pd.notna(x) else {})

df["APIResponse_dict"] = df["APIResponse"].apply(lambda x: json.loads(x) if pd.notna(x) else {})

# DYNAMIC EXTRACTION
def extract_req_res(row):
    api = row["APIName"]

    if api not in API_MAPPING:
        return pd.Series([None, None])

    req_key = API_MAPPING[api]["RequestKey"]
    res_key = API_MAPPING[api]["ResponseKey"]

    request_obj = row["APIRequest_dict"].get(req_key)
    response_obj = row["APIResponse_dict"].get(res_key)

    return pd.Series([request_obj, response_obj])

df[["Request", "Response"]] = df.apply(
    extract_req_res, axis=1
)

# FINAL OUTPUT
df_final = df[["CaseId","LgId","MarkCompleteDateTime","ReportDateTime","CaseStatus","APIName","Request","Response"]]
df_final = df_final[~df_final["Response"].astype(str).str.contains(r"'ResponseCode':\s*'108'", na=False)]

# EXPORT TO EXCEL
OUTPUT_EXCEL_PATH = r"C:\Users\kpras\Desktop\API_Extracted_Output.xlsx"
df_final.to_excel(r"C:\Users\kpras\Desktop\API_Extracted_Output.xlsx",index=False,engine="xlsxwriter")

if os.path.exists(JSON_PATH):
    os.remove(JSON_PATH)
else:
    print("File does not exist")

print(f"Excel file created at: {OUTPUT_EXCEL_PATH}")