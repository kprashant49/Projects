import openai
import pandas as pd
import requests

filepath = r"C:\Users\kpras\Desktop\pincodes_nf.xlsx"
df = pd.read_excel(filepath,sheet_name='Sheet1', engine = 'openpyxl')
GOOGLE_API_KEY = 'AIzaSyBxpjmBBn1vhY_iJ2aLYGBd4udbiKdING8'

openai.api_key = "lm-studio"
openai.api_base = "http://localhost:1234/v1"

def fix_address(raw):
    prompt = f"Fix and complete this Indian address for geolocation, please also remove any zip code previously available in the address. \
    Try to catch the area and city from the address. Strictly, provide only address as prompt output: '{raw}'"
    response = openai.ChatCompletion.create(
        model="google/gemma-3-12b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message["content"].strip()

df["Fixed_address"] = df["Address"].apply(fix_address)

def get_pincode_google(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': address,
        'key': GOOGLE_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                for component in results[0]["address_components"]:
                    if "postal_code" in component["types"]:
                        return component["long_name"]
        return "Not found"
    except Exception as e:
        return str(e)

df["Pincode"] = df["Fixed_address"].apply(get_pincode_google)
# df["Pincode"] = df["Address"].apply(get_pincode_google)
df.to_excel(r"C:\Users\kpras\Desktop\pincodes_output.xlsx", index=False)
print(df)