import pandas as pd
from sqlalchemy import create_engine
import json
with open('db_config.json') as f:
    config = json.load(f)

host=config["host"]
user=config["user"]
password=config["password"]
database=config["database"]

# Create SQLAlchemy engine
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

# data = {
#     "id": [1, 2, 3],
#     "name": ["Alice", "Bob", "Charlie"],
#     "age": [25, 30, 35]
# }
# df = pd.DataFrame(data)

new_data = {
    "id": [6, 7],  # Make sure ID is unique if it's a PRIMARY KEY
    "name": ["Scott", "Emily"],
    "age": [22, 25]
}
df_new = pd.DataFrame(new_data)

# Insert data into MySQL table
# df.to_sql("users", con=engine, if_exists="append", index=False)
df_new.to_sql("users", con=engine, if_exists="append", index=False)

# print("Data inserted successfully!")
print("New data appended successfully!")