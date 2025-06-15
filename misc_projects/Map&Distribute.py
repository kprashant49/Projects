import pandas as pd
import mysql.connector
import itertools
import json

filepath_input = r"C:\Users\kpras\Desktop\Allocation.xlsx"
df = pd.read_excel(filepath_input,sheet_name='Sheet1', engine = 'openpyxl')
table_a_1 = df[['AGREEMENTID','MAILINGZIPCODE']]

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
table_b_1 = pd.DataFrame(rows, columns=columns)

# Input Tables
table_a = pd.DataFrame({
    'id_a': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8'],
    'common_key': ['X', 'X', 'Y', 'Y', 'X', 'X', 'X', 'X']
})
table_b = pd.DataFrame({
    'id_b': ['B1', 'B2', 'B3', 'B4', 'B5'],
    'common_key': ['X', 'X', 'X', 'Y', 'Z']
})
result = []

# Loop by common_key
for key in set(table_a['common_key']) & set(table_b['common_key']):
    a_group = table_a[table_a['common_key'] == key]
    b_group = table_b[table_b['common_key'] == key]

    b_cycle = itertools.cycle(b_group['id_b'].tolist())

    for idx, row in a_group.iterrows():
        result.append({
            'index': idx,  # capture original index
            'id_a': row['id_a'],
            'id_b': next(b_cycle),
            'common_key': key
        })

mapped_df = pd.DataFrame(result).set_index('index').sort_index().reset_index(drop=True)

print(table_a)
print(table_b)
print(mapped_df)
