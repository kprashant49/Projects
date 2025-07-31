import requests
import json

# Define the API endpoint
url = " https://ifsc.razorpay.com/IDFB0021171"

# Make the GET request
response = requests.get(url)

# Check if the request was successful
# if response.status_code == 200:
#     data = response.json()  # Convert response to JSON
#     print("Response Data:", data)

if response.status_code == 200:
    data = response.json()  # Convert response to JSON
    print("Response Data (Beautified):")
    print(json.dumps(data, indent=4))  # Beautify JSON output

else:
    print("Failed to fetch data. Status code:", response.status_code)
