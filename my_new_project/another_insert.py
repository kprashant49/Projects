from sqlalchemy import create_engine, text
import pandas as pd

# Database connection details
host = "localhost"
user = "root"
password = "Punjab1$"
database = "mynewproject"

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Establish connection
with engine.connect() as conn:
    print("Connected to MySQL successfully!")

create_table_query = """
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    product_name VARCHAR(100),
    amount DECIMAL(10,2) );
"""

# Execute the query
with engine.connect() as conn:
    conn.execute(text(create_table_query))
    print("Table 'orders' created successfully!")

# Sample data
insert_query = """
INSERT INTO orders (user_id, product_name, amount) VALUES
(1, 'Laptop', 1200.50),
(2, 'Phone', 800.00),
(2, 'Tablet', 500.00),
(3, 'Monitor', 300.00),
(4, 'Headphones', 150.00);
"""

# Execute the query
with engine.connect() as conn:
    conn.execute(text(insert_query))
    conn.commit()  # Commit the transaction
    print("Sample data inserted into 'orders' table!")


# Query to retrieve data
query = "SELECT * FROM orders"

# Read data into Pandas DataFrame
df = pd.read_sql(query, con=engine)

# Display DataFrame
print(df)
