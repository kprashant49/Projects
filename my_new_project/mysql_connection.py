import pymysql
import json

with open('db_config.json') as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    database=config["database"]
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM tracker_data")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
