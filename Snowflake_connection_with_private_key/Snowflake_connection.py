import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
load_dotenv()

PRIVATE_KEY_PATH = r"D:\Projects\Snowflake_connection_with_private_key\rsa_key_snowflake.pem"
with open(PRIVATE_KEY_PATH, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,  # Provide password if PEM is encrypted
        backend=default_backend()
    )

private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=os.environ["user"],
        account=os.environ["account"],
        warehouse=os.environ["warehouse"],
        database=os.environ["database"],
        schema=os.environ["schema"],
        autocommit=True,
        role=os.environ["role"],
        private_key=private_key_bytes  # Using private key authentication
    )

def run_query(query):
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

# Example usage:
query = "select * from raw.mis_data.transaction_pai"
result = run_query(query)
print(result)