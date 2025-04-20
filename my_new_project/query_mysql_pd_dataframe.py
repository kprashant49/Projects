import pandas as pd
from sqlalchemy import create_engine

# Database connection details
host = "localhost"
user = "root"
password = "Punjab1$"
database = "mynewproject"

# Create engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Correct way to use `pd.read_sql()`
query = "SELECT * FROM users a, orders b where a.id = b.user_id;"  # Example query
df = pd.read_sql(query, con=engine)  # Pass both the query and the connection

# Display DataFrame
# print(df)
counts = df.groupby('name').count()
print(counts)