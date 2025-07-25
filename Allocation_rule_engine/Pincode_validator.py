import pandas as pd
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_pincode(address):
    url = "http://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'MyApp/1.0 (your.email@example.com)'
    }
    params = {
        'format': 'json',
        'q': address,
        'addressdetails': 1,
        'limit': 1
    }

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['address'].get('postcode', 'Pincode not found')
            else:
                return "No result"
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return str(e)

data = {
    'Address': [
        'BUILDING NO 34 ROOM NO 4 KAVERI NAGAR POLICE LINE NR PRATHAN SOC WAKWAD HINJEWADI, Pune, India',
        'Sutarwadi, Pashan, Pune, India',
        'Camp, Pune, India',
        'Kothrud, Pune, India'
    ]
}

df = pd.DataFrame(data)
df['Pincode'] = df['Address'].apply(lambda x: get_pincode(x))
# df.to_excel(r"C:\Users\kpras\Desktop\pincodes_output.xlsx", index=False)
print(df)