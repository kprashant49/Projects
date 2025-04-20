import mysql.connector
import pandas as pd
import json

with open('db_config.json') as f:
    config = json.load(f)

conn = mysql.connector.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)
cursor = conn.cursor()

update_data = {
    "id": [1, 2],
    "name": ["Alice", "Bob"],
    "age": [26, 31]
}
df_update = pd.DataFrame(update_data)

# Loop through DataFrame and update MySQL
for _, row in df_update.iterrows():
    sql = "UPDATE users SET name = %s, age = %s WHERE id = %s"
    values = (row['name'], row['age'], row['id'])
    cursor.execute(sql, values)

conn.commit()  # Commit changes
cursor.close()
conn.close()

print("Data updated successfully!")

