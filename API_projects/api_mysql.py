from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
import pymysql
import pandas as pd
import json

# Database connection details
with open('../Database_interaction_projects/db_config.json') as f:
    config = json.load(f)

host=config["host"]
user=config["user"]
password=config["password"]
database=config["database"]

# Initialize FastAPI
app = FastAPI()


# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Route to fetch all data
@app.get("/rto_data")
def get_rto():
    query = "SELECT * FROM RTO_DATA;"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
    return {"data": [dict(zip(columns, row)) for row in rows]}

# Route to fetch a specific data by ID
@app.get("/rto_data/{rto_no}")
def get_rto_no(rto_no: str):
    query = "SELECT * FROM RTO_DATA WHERE REGISTRATION_NUMBER = :rto_no;"
    with engine.connect() as conn:
        result = conn.execute(text(query), {'rto_no': rto_no})
        row = result.fetchone()
    if row:
        return dict(zip(result.keys(), row))
    return {"message": "RTO not found"}

# Route to query the data manually
@app.get("/query/{user_query}")
def get_query(user_query: str):
    query = user_query
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
    # Raise an exception if no data is found
    if not rows:
        raise HTTPException(status_code=404, detail="No data found")
    return {"data": [dict(zip(columns, row)) for row in rows]}

# Run the API with: uvicorn api_mysql:app --reload (using cmd prompt in the python script located folder)
# To terminate the server type Ctrl + C