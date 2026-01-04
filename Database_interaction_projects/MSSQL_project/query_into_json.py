import pyodbc
import json
import os

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