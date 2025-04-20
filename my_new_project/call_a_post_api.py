import requests
import json

# Define the API endpoint
url = "https://dajb7mg2pc.execute-api.ap-south-1.amazonaws.com/prashant/api/v1/calculateEMI"

# Define the payload (data to send)
payload = {
    "Product_Id": 5000382,
    "PF_Type": "rate",
    "onroadprice": "82618",
    "LI_insurance": "N",
    "dob": "11/05/2000",
    "PA": "N",
    "statecode": "19",
    "loanservicingcharge": 425,
    "vechicleinsurancebywemi": 0,
    "rtobywemi": 0,
    "processingfee": 4.75,
    "ROI": "14.99",
    "advanceemi": 1,
    "tenure": "18",
    "downpayment": 45957,
    "DCM": 1100,
    "NACH": 0,
    "CPA_RTO_Penalty": 0,
    "otherscharges": 700,
    "SEORP": 0,
    "permisiibleLTV": 0,
    "managerincentive": 0,
    "subventioncharge": 0,
    "documantationcharge": 0,
    "holdfornoc": 0,
    "holdfordrc": 0,
    "fcamount": 0,
    "riskpoolcharge": 0,
    "slabid": 1
}

# Define headers (optional, but useful for APIs expecting JSON data)
headers = {"Content-Type": "application/json"}

# Make the POST request
response = requests.post(url, data=json.dumps(payload), headers=headers)

# Check if the request was successful
if response.status_code in [200, 201]:  # 201 means "Created"
    data = response.json()  # Convert response to JSON
    print("Response Data (Beautified):")
    print(json.dumps(data, indent=4))  # Beautify JSON output
else:
    print("Failed to create post. Status code:", response.status_code)
