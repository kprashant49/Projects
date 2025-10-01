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
# query = "SELECT * FROM pincode_master;"  # Example query
# query = "Select reverse(upper('Why does my cat looks at me with such hatred?'))"
# query = "Select replace(title,' ','->') as title from books"
# query = "Select author_fname as forward, reverse(author_fname) as backwards from books"
query = "Select upper(concat(author_fname,' ',author_lname)) as FULLNAME from books"

df = pd.read_sql(query, con=engine)  # Pass both the query and the connection

# Display DataFrame
print(df)
# counts = df.groupby('name').count()
# print(counts)
# df.to_excel(r"C:\Users\kpras\Desktop\Pincode_Master.xlsx", index=False)