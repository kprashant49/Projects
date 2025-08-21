from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import pandas as pd
import uvicorn
from DB_chatbot import build_sql_from_input, db_connection

app = FastAPI()


@app.get("/query")
def run_query(q: str = Query(..., description="User natural language query")):
    """API endpoint to fetch DB results from user natural language input."""
    try:
        sql_query = build_sql_from_input(q)
        print("Generated Query:", sql_query)

        conn = db_connection()
        if conn is None:
            return JSONResponse(status_code=500, content={"error": "Database connection failed"})

        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        cursor.close()
        conn.close()

        df = pd.DataFrame(rows, columns=columns)
        return df.to_dict(orient="records")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run("API_wrapper:app", host="0.0.0.0", port=8000, reload=True)
