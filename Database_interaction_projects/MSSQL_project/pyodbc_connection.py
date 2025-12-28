import pyodbc
import json
import os

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

DB = config["DB"]
OUTPUT_PATH = config["OUTPUT_PATH"]
QUERY = config["QUERY"]

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

# Get column names
# columns = [column[0] for column in cursor.description]

# Convert rows to list of dicts
# data = [dict(zip(columns, row)) for row in cursor.fetchall()]

final_data = []

for application_no, request_json in cursor.fetchall():
    parsed_json = json.loads(request_json)      # parse JSON string
    base64_pdf = parsed_json.get("vendor_pdf") # extract only base64

    if base64_pdf:
        final_data.append({
            "ApplicationNo": application_no,
            "vendor_pdf": base64_pdf
        })

# Convert to JSON string
json_output = json.dumps(final_data, indent=2, default=str)

# Ensure directory exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Save JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(json_output)

print(json_output)
print(f"JSON saved at: {OUTPUT_PATH}")

cursor.close()
conn.close()