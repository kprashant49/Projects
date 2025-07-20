import requests

url = "https://frwwdde-aw10723.snowflakecomputing.com"
try:
    r = requests.get(url)
    print("Status Code:", r.status_code)
except Exception as e:
    print("Connection failed:", e)
