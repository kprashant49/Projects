import pandas as pd
from collections import defaultdict
import mysql.connector
import json

# Importing current month's allocation
filepath_input = r"C:\Users\kpras\Desktop\Test_data\Allocation.xlsx"
df = pd.read_excel(filepath_input,sheet_name='Sheet1', engine = 'openpyxl')
table_a = df[['AGREEMENTID', 'MAILINGZIPCODE']]

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
merged_df1 = pd.merge(table_a, df_allocation, how='left', on='AGREEMENTID', indicator=True)
merged_df2 = merged_df1[merged_df1['_merge'] == 'both']
merged_df2['_merge'] = 'Assigned basis old allocation'
merged_df2.rename(columns={'_merge': 'Allocation_Status'}, inplace=True)
# Create a counter column that increments per AWS_CODE
merged_df2['FOS_mapping_count'] = merged_df1.groupby('AWS_CODE').cumcount() + 1
merged_df2['MAILINGZIPCODE'] = merged_df2['MAILINGZIPCODE'].astype(str)
merged_df2 = merged_df2.dropna()

exclusive_A = merged_df1[merged_df1['_merge'] == 'left_only']
exclusive_A = exclusive_A[table_a.columns]

# Preparing for agent mapping
cursor = conn.cursor()
cursor.execute("SELECT MAILINGZIPCODE, AWS_CODE, FOS_NAME FROM pai_emp_pincode_mapper")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
cursor.close()
conn.close()
table_b = pd.DataFrame(rows, columns=columns)

# Convert ZIP codes to string and strip any leading/trailing spaces
exclusive_A = exclusive_A[['AGREEMENTID', 'MAILINGZIPCODE']].copy()
exclusive_A['MAILINGZIPCODE'] = exclusive_A['MAILINGZIPCODE'].astype(str).str.strip()
table_b['MAILINGZIPCODE'] = table_b['MAILINGZIPCODE'].astype(str).str.strip()

# Pre-existing mapping counts (can be empty!)
# existing_counts = {'431': 30}
merged_df2['AWS_CODE'].value_counts()
existing_counts = merged_df2['AWS_CODE'].value_counts().to_dict()

# Safe default to 0 if key not present
assignment_counter = defaultdict(int, existing_counts)
result = []

# Assign A rows to least-loaded B rows for each common_key
for idx, row in exclusive_A.iterrows():
    key = row['MAILINGZIPCODE']

    # Get all matching B rows for this key
    b_group = table_b[table_b['MAILINGZIPCODE'] == key]['AWS_CODE'].tolist()

    if not b_group:
        # No matching B for this A — skip or assign None
        result.append({
            'index': idx,
            'AGREEMENTID': row['AGREEMENTID'],
            'MAILINGZIPCODE': key,
            'AWS_CODE': None,
            'Allocation_Status': 'OGL',
            'FOS_mapping_count': None
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
        'AWS_CODE': min_b,
        'Allocation_Status': 'Assigned by rule_engine',
        'FOS_mapping_count': assignment_counter[min_b]
    })

mapped_df2 = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)
mapped_df3 = pd.concat([merged_df2, mapped_df2], ignore_index=True)
mapped_df3['AGREEMENTID'] = mapped_df3['AGREEMENTID'].astype(str)
table_a['AGREEMENTID'] = table_a['AGREEMENTID'].astype(str)
mapped_df3['AGREEMENTID'] = pd.Categorical(mapped_df3['AGREEMENTID'], categories=table_a['AGREEMENTID'], ordered=True)
df2_sorted = mapped_df3.sort_values('AGREEMENTID')
# df2_sorted.drop('FOS_mapping_count', axis=1, inplace=True)
df2_sorted.to_excel(r"C:\Users\kpras\Desktop\Auto_allocation.xlsx", index=False)
print("Exported the output to an excel file named 'Auto_allocation.xlsx'")