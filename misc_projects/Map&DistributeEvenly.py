import pandas as pd
from collections import defaultdict
import mysql.connector
import json

# Importing current month's allocation
filepath_input = r"C:\Users\kpras\Desktop\Test_data\Allocation.xlsx"
allocation_new = pd.read_excel(filepath_input,sheet_name='Sheet1', engine = 'openpyxl')
df_allocation_new = allocation_new[['AGREEMENTID', 'MAILINGZIPCODE']]

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
df_allocation_old = pd.DataFrame(rows, columns=columns)

# Priority 1 mapping
df_allocation_new['AGREEMENTID'] = df_allocation_new['AGREEMENTID'].astype(str)
df_allocation_old['AGREEMENTID'] = df_allocation_old['AGREEMENTID'].astype(str)
df_map_priority1 = pd.merge(df_allocation_new, df_allocation_old, how='left', on='AGREEMENTID', indicator=True)
df_priority1 = df_map_priority1[df_map_priority1['_merge'] == 'both']
df_priority1['_merge'] = 'Assigned basis old allocation'
df_priority1.rename(columns={'_merge': 'Allocation_Status'}, inplace=True)

# Create a counter column that increments per AWS_CODE
df_priority1['FOS_mapping_count'] = df_map_priority1.groupby('AWS_CODE').cumcount() + 1
df_priority1['MAILINGZIPCODE'] = df_priority1['MAILINGZIPCODE'].astype(str)
df_priority1 = df_priority1.dropna()

df_non_map_priority1 = df_map_priority1[df_map_priority1['_merge'] == 'left_only']
df_non_map_priority1 = df_non_map_priority1[df_allocation_new.columns]

# Loading data for Priority 2 mapping
cursor = conn.cursor()
cursor.execute("SELECT MAILINGZIPCODE, AWS_CODE, FOS_NAME FROM pai_emp_pincode_mapper")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
cursor.close()
conn.close()
employee_pincode_mapper = pd.DataFrame(rows, columns=columns)

df_non_map_priority1 = df_non_map_priority1[['AGREEMENTID', 'MAILINGZIPCODE']].copy()
df_non_map_priority1['MAILINGZIPCODE'] = df_non_map_priority1['MAILINGZIPCODE'].astype(str).str.strip()
employee_pincode_mapper['MAILINGZIPCODE'] = employee_pincode_mapper['MAILINGZIPCODE'].astype(str).str.strip()

# Calculating FOS mapping counts after Priority 1 mapping and assigning it to a dictionary for multi-counters (can be empty!)
# Using default dictionary for safe default to 0 if FOS not present
# existing_counts = {'431': 30}
df_priority1['AWS_CODE'].value_counts()
existing_counts = df_priority1['AWS_CODE'].value_counts().to_dict()
assignment_counter = defaultdict(int, existing_counts)
result = []

# Assign AgreementID rows to least-loaded FOS rows for each Zipcode
for idx, row in df_non_map_priority1.iterrows():
    key = row['MAILINGZIPCODE']

    # Get all matching FOS rows for this Zipcode
    fos_group = employee_pincode_mapper[employee_pincode_mapper['MAILINGZIPCODE'] == key]['AWS_CODE'].tolist()

    if not fos_group:
        # No matching FOS for this Zipcode — skip or assign None
        result.append({
            'index': idx,
            'AGREEMENTID': row['AGREEMENTID'],
            'MAILINGZIPCODE': key,
            'AWS_CODE': 'No FOS',
            'Allocation_Status': 'OGL',
            'FOS_mapping_count': None
        })
        continue

    # Find least-loaded FOS based on current + existing mapping
    # min_fos = min(fos_group, key=lambda x: assignment_counter[x]) - Another method
    min_count = None
    min_fos = None
    for x in fos_group:
        count = assignment_counter[x]
        if min_count is None or count < min_count:
            min_count = count
            min_fos = x
    # Assign and update counter
    assignment_counter[min_fos] += 1

    result.append({
        'index': idx,
        'AGREEMENTID': row['AGREEMENTID'],
        'MAILINGZIPCODE': key,
        'AWS_CODE': min_fos,
        'Allocation_Status': 'Assigned by rule_engine',
        'FOS_mapping_count': assignment_counter[min_fos]
    })

df_priority2 = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)
allocation_combined = pd.concat([df_priority1, df_priority2], ignore_index=True)
allocation_combined['AGREEMENTID'] = allocation_combined['AGREEMENTID'].astype(str)
allocation_combined['AGREEMENTID'] = pd.Categorical(allocation_combined['AGREEMENTID'], categories=df_allocation_new['AGREEMENTID'], ordered=True)
Auto_allocation = allocation_combined.sort_values('AGREEMENTID')
# Auto_allocation.drop('FOS_mapping_count', axis=1, inplace=True)
Auto_allocation.to_excel(r"C:\Users\kpras\Desktop\Auto_allocation.xlsx", index=False)
print("Exported the output to an excel file named 'Auto_allocation.xlsx'")