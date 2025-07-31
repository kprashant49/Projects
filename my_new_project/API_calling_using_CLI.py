import argparse
import requests
import json

# ---------- Configuration ----------

get_api_url = "https://ifsc.razorpay.com/IDFB0021171"

post_api_url = "https://avs3y2st17.execute-api.ap-south-1.amazonaws.com/prod/api/v1/calculateEMI"
post_payload = {
    "vechicleinsurancebywemi":0,
    "tenure":"12",
    "subventioncharge":0.00,
    "statecode":"06",
    "slabid":0,
    "SEORP":92914.00,
    "rtobywemi":0,
    "ROI":"0.00",
    "riskpoolcharge":0,
    "Product_Id":5000383,
    "processingfee":3750.0,
    "PF_Type":"flat",
    "permisiibleLTV":200,
    "PAinsurance":0,
    "PA":"Y",
    "otherscharges":100.00,
    "onroadprice":92000.00,
    "NACH":600.00,
    "managerincentive":0,
    "loanservicingcharge":425,
    "lifeinsurance":0,
    "LI_insurance":"Y",
    "holdfornoc":0,
    "holdfordrc":7000,
    "gender":"Male",
    "fcamount":0,
    "downpayment":70000,
    "documentationcharge":0,
    "dob":"04/04/1986",
    "DCM":0.00,
    "CPA_RTO_Penalty":0,
    "advanceemi":0
}
post_headers = {"Content-Type": "application/json"}


# ---------- API Functions ----------

def call_get_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("GET API Response:")
        print(json.dumps(data, indent=4))
    else:
        print(f"GET API failed. Status Code: {response.status_code}")


def call_post_api(url, payload, headers):
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code in [200, 201]:
        data = response.json()
        print("POST API Response:")
        print(json.dumps(data, indent=4))
    else:
        print(f"POST API failed. Status Code: {response.status_code}")


# ---------- CLI Parser ----------

def main():
    parser = argparse.ArgumentParser(description="Call GET or POST API.")
    parser.add_argument("method", choices=["get", "post"], help="HTTP method to call")

    args = parser.parse_args()

    if args.method == "get":
        call_get_api(get_api_url)
    elif args.method == "post":
        call_post_api(post_api_url, post_payload, post_headers)

if __name__ == "__main__":
    main()
