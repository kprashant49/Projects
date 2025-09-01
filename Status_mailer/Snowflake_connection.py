import configparser
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def load_config(config_path='config.ini', section='Snowflake'):
    """Loads configuration values from the config.ini file."""
    config = configparser.ConfigParser()
    config.read(config_path)
    return config[section]

def load_private_key(key_path, passphrase=None):
    """Loads a PEM-format RSA private key."""
    with open(key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=passphrase.encode() if passphrase else None,
            backend=default_backend()
        )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def get_snowflake_connection(config_section):
    private_key = load_private_key(config_section['private_key_path'])

    connection = snowflake.connector.connect(
        user=config_section['user'],
        account=config_section['account'],
        warehouse=config_section['warehouse'],
        database=config_section['database'],
        schema=config_section['schema'],
        role=config_section['role'],
        autocommit=config_section.getboolean('autocommit'),
        private_key=private_key
    )
    return connection

def get_cursor(config):
    conn = get_snowflake_connection(config)
    return conn, conn.cursor()

def run_query(query, config):
    conn = get_snowflake_connection(config)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    finally:
        cursor.close()
        conn.close()

# ----------- MAIN SCRIPT EXECUTION ------------

if __name__ == "__main__":
    config = load_config('config.ini')

    query = "select * from prd.analytics.marts_retail_idfc"
    result = run_query(query, config)

    for row in result:
        print(row)

