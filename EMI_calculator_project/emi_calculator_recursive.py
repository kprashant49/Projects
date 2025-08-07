# emi_calculator.py
import os
import math
import requests
from fastapi import APIRouter
from utils import Errorapiresponse

router = APIRouter()

# --- Flat EMI Calculation ---
def flat_emi(p, r, t):
    return math.ceil((p + (p * (r / 100) * t) / 12) / t)

# --- Premium Calculation (Life Insurance) ---
def get_premium(tenure, nfa):
    if nfa < 5000 or nfa > 200000:
        return 0
    if 0 < tenure <= 12:
        return math.ceil(nfa * 0.004)
    elif 12 < tenure <= 24:
        return math.ceil(nfa * 0.008)
    elif 24 < tenure <= 36:
        return math.ceil(nfa * 0.014)
    return 0

# --- PA Amount Calculation ---
def get_pa_amount(tenure):
    if tenure <= 12:
        return 719
    elif 12 < tenure <= 24:
        return 371
    elif 24 < tenure <= 36:
        return 399
    return 0

# --- PF Type Validation ---
def validate_pf_type(pf_type):
    pf_type_clean = str(pf_type).strip().lower()
    if pf_type_clean in ["flat", "rate", "hybrid"]:
        return pf_type_clean
    return "flat"

# --- Safe Dictionary Lookup ---
def safe_pf_lookup(pf_type):
    PF_TYPE_MAP = {
        "flat": 0,
        "rate": 0.02,
        "hybrid": 0.025
    }
    return PF_TYPE_MAP.get(pf_type, PF_TYPE_MAP["flat"])

# --- Hybrid PF API ---

async def calculate_hybrid_pf(slabid, nfa, res):
    try:
        payload = {"Slab_Id": slabid, "Amount_Finacne": nfa}
        url = os.environ.get("u2w_process_fees")
        headers = {"Authorization": os.environ.get("API_TOKEN")}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if str(data.get("Success")).lower() == "true":
            return data["Message"].get("Processing_Fees")
        return res(Errorapiresponse("006"))
    except Exception as e:
        print("U2W PF API Error:", e)
        return res(Errorapiresponse("012"))

# --- Stamp Duty API ---
async def get_stamp_duty(nfa, statecode, res):
    try:
        payload = {"Amount_Finacne": nfa, "State_Code": statecode}
        url = os.environ.get("stamp_duty_charge_api")
        headers = {"Authorization": os.environ.get("API_TOKEN")}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        print("DEBUG:: stamp duty response =>", data)
        success = str(data.get("Success")).lower() == "true"
        message = data.get("Message", {})
        duty = message.get("stamp_duty_charge") if isinstance(message, dict) else None
        return [{"stumpdutyamount": duty}] if success and duty is not None else res(Errorapiresponse("005"))
    except Exception as e:
        print("Stamp Duty API Error:", e)
        return res(Errorapiresponse("011"))

# --- Calculate All (NewTW) ---
async def calculate_all(payload, res):
    try:
        pf_type = validate_pf_type(payload["PF_Type"])
        onroadprice = float(payload["onroadprice"])
        advanceemi = float(payload["advanceemi"])
        stampduty = float(payload["stampduty"])
        rate = float(payload.get("rate", payload.get("ROI", 0)))
        tenure = int(payload["tenure"])
        processingfee = float(payload["processingfee"])
        downpayment = float(payload["downpayment"])
        totaldeductiondecutible = float(payload["totaldeductiondecutible"])
        totaldeductionreceiveable = float(payload["totaldeductionreceiveable"])
        slabid = int(payload.get("slabid", 0))

        nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty
        iteration = 0

        if pf_type == "hybrid":
            pf = await calculate_hybrid_pf(slabid, nfa, res)
            while True:
                newpf = await calculate_hybrid_pf(slabid, nfa + pf, res)
                if pf == newpf:
                    break
                pf = newpf

        elif pf_type == "rate":
            cdp = 0
            firstcdp = 0
            while True:
                if iteration > 0:
                    firstcdp = cdp
                pf = round((nfa * processingfee) / 100)
                llemi = round(flat_emi(nfa, rate, tenure))
                cdp = onroadprice - nfa + pf + stampduty + (llemi * advanceemi)
                nfa = nfa + cdp - downpayment + totaldeductiondecutible
                if abs(firstcdp - cdp) < 0.00001 and iteration > 0:
                    break
                iteration += 1

        elif pf_type == "flat":
            pf = round(processingfee)
            nfa += pf
        else:
            return res(Errorapiresponse("009"))

        localflatemi = flat_emi(nfa, rate, tenure)
        firstemi = localflatemi
        iteration = 0

        while True:
            if iteration > 0:
                firstemi = localflatemi

            localdeductionreceiveable = (
                    stampduty + pf + round(localflatemi) * advanceemi + totaldeductionreceiveable
            )
            nfa = (
                    onroadprice - downpayment + totaldeductiondecutible + localdeductionreceiveable
            )

            if pf_type == "hybrid":
                pf = round(await calculate_hybrid_pf(slabid, nfa, res))
            elif pf_type == "rate":
                pf = round((nfa * processingfee) / 100)
            else:
                pf = round(processingfee)

            localflatemi = flat_emi(nfa, rate, tenure)

            if abs(localflatemi - firstemi) < 1:
                break

            iteration += 1

        premium = get_premium(tenure, nfa) if payload.get("LI_insurance") == "Y" else 0
        pa_amount = get_pa_amount(tenure) if payload.get("PA") == "Y" else 0

        return {
            "nfa": round(nfa + premium + pa_amount),
            "newpf": round(pf),
            "localflatemi": round(localflatemi),
            "localdeductionreceiveable": round(localdeductionreceiveable),
            "Premium": premium,
            "PAAmount": pa_amount
        }

    except Exception as e:
        print("Error in calculate_all:", e)
        return res(Errorapiresponse("012"))

# --- Calculate All RFV ---
async def calculate_all_rfv(payload, res):
    try:
        pf_type = validate_pf_type(payload["PF_Type"])
        onroadprice = float(payload["onroadprice"])
        advanceemi = float(payload["advanceemi"])
        stampduty = float(payload["stampduty"])
        rate = float(payload.get("rate", payload.get("ROI", 0)))
        tenure = int(payload["tenure"])
        processingfee = float(payload["processingfee"])
        totaldeductiondecutible = float(payload["totaldeductiondecutible"])
        totaldeductionreceiveable = float(payload["totaldeductionreceiveable"])
        slabid = int(payload.get("slabid", 0))

        nfa = onroadprice + totaldeductiondecutible

        if pf_type == "hybrid":
            pf = await calculate_hybrid_pf(slabid, nfa, res)
            while True:
                newpf = await calculate_hybrid_pf(slabid, nfa + pf, res)
                if pf == newpf:
                    break
                pf = newpf
        elif pf_type == "rate":
            prev_nfa = -1
            while True:
                pf = round((nfa * processingfee) / 100)
                emi = round(flat_emi(nfa, rate, tenure))
                nfa = onroadprice + totaldeductiondecutible + emi * advanceemi
                if abs(nfa - prev_nfa) < 0.00001:
                    break
                prev_nfa = nfa
        elif pf_type == "flat":
            pf = round(processingfee)
        else:
            return res(Errorapiresponse("010"))

        localflatemi = flat_emi(nfa, rate, tenure)
        localdeductionreceiveable = (
            round(localflatemi) * advanceemi + stampduty + pf + totaldeductionreceiveable
        )

        return {
            "nfa": round(nfa),
            "newpf": round(pf),
            "localflatemi": round(localflatemi),
            "localdeductionreceiveable": round(localdeductionreceiveable)
        }

    except Exception as e:
        print("Error in calculate_all_rfv:", e)
        return res(Errorapiresponse("012"))


# --- Dynamic Calculation Block (Core Recursive Logic) ---
async def recalculate_all_values(payload, res_handler, calc_fn):
    iteration = 1
    previous_nfa = -1
    result = None

    while True:
        result = await calc_fn(payload.copy(), res_handler)
        if not result:
            return res_handler(Errorapiresponse("012"))

        tenure = int(payload.get("tenure", 0))
        rate = float(payload.get("ROI", 0))

        premium = get_premium(tenure, result["nfa"]) if payload.get("LI_insurance") == "Y" else 0
        pa_amount = get_pa_amount(tenure) if payload.get("PA") == "Y" else 0

        new_nfa = result["nfa"] + premium + pa_amount
        if abs(new_nfa - previous_nfa) < 1:
            break

        print(f"DEBUG:: Iteration {iteration} => Old NFA: {result['nfa']}, Premium: {premium}, PA: {pa_amount}, New NFA: {new_nfa}")

        payload["nfa"] = new_nfa
        previous_nfa = new_nfa
        iteration += 1

    result["Premium"] = premium
    result["PAAmount"] = pa_amount
    result["nfa"] = new_nfa
    result["localflatemi"] = flat_emi(new_nfa, rate, tenure)
    return result

# --- EMI Endpoint ---
@router.post("/calculate-emi")
async def calculate_emi_endpoint(payload: dict):
    try:
        res_handler = lambda err: err

        payload["PF_Type"] = validate_pf_type(payload.get("PF_Type"))
        payload["totaldeductiondecutible"] = float(payload.get("totaldeductiondecutible", 0))
        payload["totaldeductionreceiveable"] = 0

        stamp_duty_result = await get_stamp_duty(float(payload["onroadprice"]), payload["statecode"], res_handler)
        if not stamp_duty_result or not isinstance(stamp_duty_result, list):
            return Errorapiresponse("005")

        stamp_duty = stamp_duty_result[0]["stumpdutyamount"]
        payload["stampduty"] = stamp_duty + float(payload.get("DCM", 0)) + float(payload.get("NACH", 0)) + float(payload.get("otherscharges", 0)) + 32

        result = await calculate_all(payload.copy(), res_handler)

        tenure = int(payload.get("tenure", 0))
        advance_emi = float(payload.get("advanceemi", 0))
        onroad_price = float(payload["onroadprice"])
        seorp = float(payload["SEORP"])
        adjusted_nfa = result["nfa"] - result["localflatemi"] * advance_emi

        return {
            "Success": True,
            "Message": {
                "flatemi": result["localflatemi"],
                "Net_Finance_amount": result["nfa"],
                "deduction": result["localdeductionreceiveable"],
                "stampduty": math.ceil(stamp_duty),
                "stampdutyservicecharge": 32,
                "processingfee": result["newpf"],
                "Margin_Money": math.ceil(onroad_price - result["nfa"]),
                "disbursementamount": math.ceil(result["nfa"] - result["newpf"]),
                "Premium": result.get("Premium", 0),
                "PAAmount": result.get("PAAmount", 0),
                "LTV": round((adjusted_nfa / onroad_price) * 100, 2) if onroad_price else 0.0,
                "SELTV": round((adjusted_nfa / seorp) * 100, 2) if seorp else 0.0,
                "irr": 24.89,
                "irrwithoutcharges": 29.16
            }
        }

    except Exception as e:
        print("API error:", e)
        return Errorapiresponse("012")


