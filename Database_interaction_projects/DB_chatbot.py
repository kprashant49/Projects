import openai
import pandas as pd
import pymysql
import json

openai.api_key = "lm-studio"
openai.api_base = "http://localhost:1234/v1"


def query_builder():
    """Ask user what they want and let LLM build SQL query."""
    user_input = input("Please enter what do you wish to query? ")
    prompt = f"Build a MySQL query from this request. Output only the SQL query:\n\n'{user_input}'"

    try:
        response = openai.ChatCompletion.create(
            model="google/gemma-3-12b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error generating query:", e)
        return None


def db_connection():
    """Open a database connection from db_config.json"""
    try:
        with open('db_config.json') as f:
            config = json.load(f)

        conn = pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None


def fetch_dataframe():
    """Run query safely and return results as DataFrame."""
    conn = db_connection()
    if conn is None:
        return pd.DataFrame()  # empty dataframe

    query = query_builder()
    if not query:
        return pd.DataFrame()

    print("Generated Query:", query)

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(rows, columns=columns)

        cursor.close()
        conn.close()
        return df

    except Exception as e:
        print("SQL Execution error:", e)
        return pd.DataFrame()


if __name__ == "__main__":
    df = fetch_dataframe()
    if df.empty:
        print("No results or query failed.")
    else:
        print(df.head())