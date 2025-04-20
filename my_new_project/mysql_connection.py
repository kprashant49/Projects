import pymysql

conn = pymysql.connect(
    host="localhost",  # e.g., "localhost"
    user="root",
    password="Punjab1$",
    database="mynewproject"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM tracker_data")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
