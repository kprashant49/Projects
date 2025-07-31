import pandas as pd
from sqlalchemy import create_engine
import json
with open('db_config.json') as f:
    config = json.load(f)

host=config["host"]
user=config["user"]
password=config["password"]
database=config["database"]

# Create engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Correct way to use `pd.read_sql()`
# query = "SELECT * FROM users a, orders b where a.id = b.user_id;"  # Example query
query = "SELECT * FROM pincode_master;"  # Example query
df = pd.read_sql(query, con=engine)  # Pass both the query and the connection

# Display DataFrame
# print(df)
# counts = df.groupby('name').count()
# print(counts)
df.to_excel(r"C:\Users\kpras\Desktop\Pincode_Master.xlsx", index=False)