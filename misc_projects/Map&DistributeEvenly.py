import pandas as pd
from collections import defaultdict
import mysql.connector
import json

# Importing current month's allocation
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

# Importing previous month's allocation
cursor = conn.cursor()
cursor.execute("SELECT AGREEMENTID, AWS_CODE FROM allocation_retail where MAILINGZIPCODE  = '411021'")
rows = cursor.fetchall()
columns = [col[0] for col in cursor.description]
df_allocation = pd.DataFrame(rows, columns=columns)

table_a['AGREEMENTID'] = table_a['AGREEMENTID'].astype(str)
df_allocation['AGREEMENTID'] = df_allocation['AGREEMENTID'].astype(str)
merged_df1 = pd.merge(table_a, df_allocation, how='left', on='AGREEMENTID')
merged_df1.to_excel(r"C:\Users\kpras\Desktop\mapped_df1.xlsx", index=False)

# Preparing for agent mapping
cursor = conn.cursor()
cursor.execute("SELECT MAILINGZIPCODE, AWS_CODE, FOS_NAME FROM pai_emp_pincode_mapper")
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
    '431': 30,
}

# Safe default to 0 if key not present
assignment_counter = defaultdict(int, existing_counts)
result = []

# Assign A rows to least-loaded B rows for each common_key
for idx, row in table_a.iterrows():
    key = row['MAILINGZIPCODE']

    # Get all matching B rows for this key
    b_group = table_b[table_b['MAILINGZIPCODE'] == key]['AWS_CODE'].tolist()

    if not b_group:
        # No matching B for this A — skip or assign None
        result.append({
            'index': idx,
            'AGREEMENTID': row['AGREEMENTID'],
            'MAILINGZIPCODE': key,
            'AWS_CODE_1': None,
            'FOS_mapping_count': None,
            'Rule_Engine_Status': 'OGL'
        })
        continue

    # Find least-loaded B based on current + existing
    # min_b = min(b_group, key=lambda b: assignment_counter[b]) - Another method
    min_count = None
    min_b = None
    for b in b_group:
        count = assignment_counter[b]
        if min_count is None or count < min_count:
            min_count = count
            min_b = b
    # Assign and update count
    assignment_counter[min_b] += 1

    result.append({
        'index': idx,
        'AGREEMENTID': row['AGREEMENTID'],
        'MAILINGZIPCODE': key,
        'AWS_CODE_1': min_b,
        'FOS_mapping_count': assignment_counter[min_b],
        'Rule_Engine_Status': 'Assigned'
    })

mapped_df2 = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)
mapped_df2.to_excel(r"C:\Users\kpras\Desktop\mapped_df2.xlsx", index=False)
print("Exported to excel")