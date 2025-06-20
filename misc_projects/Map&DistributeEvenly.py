import pandas as pd
from collections import defaultdict
import mysql.connector
import json

filepath_input = r"C:\Users\kpras\Desktop\Allocation.xlsx"
df = pd.read_excel(filepath_input,sheet_name='Sheet1', engine = 'openpyxl')
table_a = df[['AGREEMENTID','MAILINGZIPCODE']]

with open('db_config.json') as f:
    config = json.load(f)

conn = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)

cursor = conn.cursor()
cursor.execute("SELECT `MAILINGZIPCODE`, `AWS CODE`, `FOS NAME` FROM pai_emp_pincode_mapper")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
cursor.close()
conn.close()
table_b = pd.DataFrame(rows, columns=columns)

# Convert ZIP codes to string and strip any leading/trailing spaces
table_a = df[['AGREEMENTID', 'MAILINGZIPCODE']].copy()
table_a['MAILINGZIPCODE'] = table_a['MAILINGZIPCODE'].astype(str).str.strip()
table_b['MAILINGZIPCODE'] = table_b['MAILINGZIPCODE'].astype(str).str.strip()

# Pre-existing mapping counts (can be empty!)
existing_counts = {
    # 'B1': 2,
    # 'B2': 0,
    # 'B3': 0,
    # 'B4': 5,
    # 'B5': 8
}

# Safe default to 0 if key not present
assignment_counter = defaultdict(int, existing_counts)

result = []

# Assign A rows to least-loaded B rows for each common_key
for idx, row in table_a.iterrows():
    key = row['MAILINGZIPCODE']

    # Get all matching B rows for this key
    b_group = table_b[table_b['MAILINGZIPCODE'] == key]['AWS CODE'].tolist()

    if not b_group:
        # No matching B for this A — skip or assign None
        result.append({
            'index': idx,
            'AGREEMENTID': row['AGREEMENTID'],
            'MAILINGZIPCODE': key,
            'AWS CODE': None,
            'FOS_mapping_count': None,
            'Rule_Engine_Status': 'OGL'
        })
        continue

    # Find least-loaded B based on current + existing
    min_b = min(b_group, key=lambda b: assignment_counter[b])

    # Assign and update count
    assignment_counter[min_b] += 1

    result.append({
        'index': idx,
        'AGREEMENTID': row['AGREEMENTID'],
        'MAILINGZIPCODE': key,
        'AWS CODE': min_b,
        'FOS_mapping_count': assignment_counter[min_b],
        'Rule_Engine_Status': 'Assigned'
    })

mapped_df = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)
print(mapped_df)
mapped_df.to_excel(r"C:\Users\kpras\Desktop\mapped_df.xlsx", index=False)