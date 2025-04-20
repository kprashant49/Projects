import mysql.connector
import pandas as pd

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Punjab1$",
    database="mynewproject"
)
cursor = conn.cursor()

update_data = {
    "id": [1, 2],
    "name": ["Alice_updated", "Bob_updated"],
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

