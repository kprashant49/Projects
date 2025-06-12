import pandas as pd
import mysql.connector
import string
import json

filepath_input = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Collection.xlsx"
df = pd.read_excel(filepath_input,sheet_name='Sheet1', engine = 'openpyxl')

assign = df['MAILINGZIPCODE']
df['MAILINGZIPCODE'] = df['MAILINGZIPCODE'].astype(str)

with open('db_config.json') as f:
    config = json.load(f)

conn = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)

cursor = conn.cursor()
cursor.execute("SHOW COLUMNS FROM employee_pincode_mapper")
columns = [col[0] for col in cursor.fetchall()]
constant = "_rule_engine"
selected_indices = [1, 2]
new_columns = []
for i, val in enumerate(columns):
    if i in selected_indices:
        new_columns.append(val + constant)
    else:
        new_columns.append(val)

all_results = []
for zip_code in assign:
    cursor.execute("SELECT * FROM employee_pincode_mapper WHERE MAILINGZIPCODE = %s limit 1", (zip_code,))
    rows = cursor.fetchall()
    all_results.extend(rows)
cursor.close()
conn.close()

result_df = pd.DataFrame(data = all_results, columns = new_columns)
result_df = result_df.drop_duplicates()
merged_df = pd.merge(df, result_df, how='left', on='MAILINGZIPCODE')
merged_df['FOS NAME_rule_engine'] = merged_df['FOS NAME_rule_engine'].fillna('OGL')
merged_df['AWS CODE_rule_engine'] = merged_df['AWS CODE_rule_engine'].fillna('OGL')

filepath_output = r"C:\Users\PrashantKumar\OneDrive - Pepper India Resolution Private Limited\Desktop\Output.xlsx"
merged_df.to_excel(filepath_output, sheet_name='Sheet1', index=False)