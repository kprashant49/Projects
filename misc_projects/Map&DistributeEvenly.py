import pandas as pd
from collections import defaultdict
import mysql.connector
import json

# filepath_input = r"C:\Users\kpras\Desktop\Allocation.xlsx"
# df = pd.read_excel(filepath_input,sheet_name='Sheet1', engine = 'openpyxl')
# table_a_1 = df[['AGREEMENTID','MAILINGZIPCODE']]
#
# with open('db_config.json') as f:
#     config = json.load(f)
#
# conn = mysql.connector.connect(
#     host=config["host"],
#     user=config["user"],
#     password=config["password"],
#     database=config["database"]
# )
#
# cursor = conn.cursor()
# cursor.execute("SELECT `AWS CODE`, `MAILINGZIPCODE`, `FOS NAME` FROM pai_emp_pincode_mapper")
# rows = cursor.fetchall()
# columns = [desc[0] for desc in cursor.description]
# cursor.close()
# conn.close()
# table_b_1 = pd.DataFrame(rows, columns=columns)

# Input tables
table_a = pd.DataFrame({
    'id_a': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15'],
    'common_key': ['X', 'X', 'Y', 'Y', 'Y', 'Y', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z', 'Z']
})

table_b = pd.DataFrame({
    'id_b': ['B1', 'B2', 'B3', 'B4', 'B5'],
    'common_key': ['X', 'X', 'Y', 'Z', 'Z']
})

# Pre-existing mapping counts (can be empty!)
existing_counts = {
    'B1': 2,
    'B2': 0,
    'B3': 0,
    'B4': 5,
    'B5': 8
}

# Safe default to 0 if key not present
assignment_counter = defaultdict(int, existing_counts)

result = []

# Assign A rows to least-loaded B rows for each common_key
for idx, row in table_a.iterrows():
    key = row['common_key']

    # Get all matching B rows for this key
    b_group = table_b[table_b['common_key'] == key]['id_b'].tolist()

    if not b_group:
        # No matching B for this A — skip or assign None
        result.append({
            'index': idx,
            'id_a': row['id_a'],
            'common_key': key,
            'id_b': None,
            'b_mapping_count': None
        })
        continue

    # Find least-loaded B based on current + existing
    min_b = min(b_group, key=lambda b: assignment_counter[b])

    # Assign and update count
    assignment_counter[min_b] += 1

    result.append({
        'index': idx,
        'id_a': row['id_a'],
        'common_key': key,
        'id_b': min_b,
        'b_mapping_count': assignment_counter[min_b]
    })

# Final output DataFrame with Table A's order
mapped_df = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)

print(table_a)
print(table_b)
print(mapped_df)
