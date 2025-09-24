import requests
import pandas as pd

# Take user input
user_input = input("Enter the stock name: ")
script_name = user_input.upper() + ".BSE"

# API call
url = "https://www.alphavantage.co/query"
response = requests.get(
    url,
    headers={"Accept": "application/json"},
    params={
        "function": "TIME_SERIES_DAILY",
        "symbol": script_name,
        "outputsize": "compact",		#full/compact
        "apikey": "4MHEY7CV1JBL6RQV"
    }
)

data = response.json()

if "Time Series (Daily)" in data:
    symbol = data["Meta Data"]["2. Symbol"]
    time_series = data["Time Series (Daily)"]

    df = pd.DataFrame.from_dict(time_series, orient="index")
    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    })

    # Convert index to datetime
    df.index = pd.to_datetime(df.index)

    # Convert values to float
    df = df.astype(float).sort_index(ascending=False)

    # Rename index header from "Date" → "Symbol"
    df.index.name = symbol   # <-- this is the trick

    print(df)
else:
    print("Error:", data.get("Error Message", "Unexpected response"))
