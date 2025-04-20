from fastapi import FastAPI, Query
import snowflake.connector

app = FastAPI()

# Snowflake connection configuration
SNOWFLAKE_CONFIG = {
    "user": "KPRASHANT49",
    "password": "KumarPapillonA3604",
    "account": "CAVKSJX-DS08600",
    # "warehouse": "your_warehouse",
    "database": "MYFIRSTPROJECT",
    "schema": "PUBLIC"
}

def query_snowflake(sql_query: str):
    """Executes a SQL query on Snowflake and returns the results."""
    try:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        return [dict(zip(columns, row)) for row in result]
    except Exception as e:
        return {"error": str(e)}


@app.get("/query")
def get_query(sql: str = Query(..., title="SQL Query", description="SQL query to execute on Snowflake")):
    """API endpoint to run a query on Snowflake."""
    result = query_snowflake(sql)
    return result

# Run the API with: uvicorn api_snowflake:app --host 0.0.0.0 --port 8000 --reload (using cmd prompt in the python script located folder)
# To terminate the server type Ctrl + C
# Test the api in postman using url: http://127.0.0.1:8000/query?sql=SELECT * FROM RTODATA;

