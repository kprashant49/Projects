import snowflake.connector
import pandas as pd
# Snowflake connection parameters
snowflake_config={
                'user': 'KPRASHANT49',
                'password': 'KumarPapillonA3604',
                'account': 'CAVKSJX-DS08600',
                'autocommit':  True
            }

# Establish a connection to Snowflake
connection = snowflake.connector.connect(**snowflake_config)
# cursor = connection.cursor()
# cursor.execute("Select * from MYFIRSTPROJECT.PUBLIC.RTODATA")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)
query = "Select * from MYFIRSTPROJECT.PUBLIC.RTO_DATA"  # Adjust limit as needed
df = pd.read_sql(query, connection)
print(df)
# df.to_csv("rto_data.csv", index=False)
# print("Data saved to rto_data.csv")