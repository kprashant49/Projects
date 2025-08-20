import openai
import pandas as pd
import pymysql
import json
import re

openai.api_key = "lm-studio"
openai.api_base = "http://localhost:1234/v1"

def query_builder():
    """Ask user what they want and let LLM build SQL query."""
    user_input = input("Please enter what do you wish to query? ")
    prompt = f"""
        You are a MySQL query generator.
        - Users will provide keywords or natural language (they may NOT know the exact column names).
        - Your job: map the keywords to the most relevant column(s) in the table.
        - Always generate a valid SQL query for MySQL.
        - If searching by keyword, use `LIKE '%keyword%'`.
        - Strictly output ONLY the SQL query for direct querying and no explanation.
        User request: "{user_input}"
        """
    try:
        response = openai.ChatCompletion.create(
            model="google/gemma-3n-e4b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        raw_sql = response.choices[0].message.content.strip()
        safe_sql = clean_sql(raw_sql)
        return safe_sql
    except ValueError as ve:
        print(ve)
        return None
    except Exception as e:
        print("Error generating query:", e)
        return None

def clean_sql(sql_text: str) -> str:
    """Remove markdown fences and return raw SQL query safely."""
    # Remove triple backticks and optional 'sql'
    sql_text = re.sub(r"```(sql)?", "", sql_text, flags=re.IGNORECASE)
    sql_text = sql_text.strip()

    # Safety filter: allow only SELECT statements
    if not sql_text.lower().startswith("select"):
        raise ValueError(f"Unsafe SQL detected: {sql_text}")
    return sql_text

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