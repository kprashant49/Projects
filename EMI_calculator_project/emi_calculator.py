# emi_calculator.py
import os
import requests
from utils import Errorapiresponse

# --- Flat EMI Calculation ---
def flat_emi(p, r, t):
    return (p + (p * (r / 100) * t) / 12) / t

# --- Hybrid PF Calculation ---
async def calculate_hybrid_pf(slabid, nfa, res):
    try:
        payload = {
            "Slab_Id": slabid,
            "Amount_Finacne": nfa
        }
        url = os.environ.get("u2w_process_fees")
        headers = {"Authorization": os.environ.get("API_TOKEN")}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get("Success"):
            return data["Message"]["Processing_Fees"]
        return res(Errorapiresponse("006"))
    except Exception as e:
        print(e)
        return res(Errorapiresponse("012"))

# --- Stamp Duty Calculation ---
async def get_stamp_duty(nfa, statecode, res):
    try:
        payload = {
            "Amount_Finacne": nfa,
            "State_Code": statecode
        }
        url = os.environ.get("stamp_duty_charge_api")
        headers = {"Authorization": os.environ.get("API_TOKEN")}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("Success") and data["Message"].get("stamp_duty_charge"):
            return [{"stumpdutyamount": data["Message"]["stamp_duty_charge"]}]
        else:
            return res(Errorapiresponse("011"))
    except Exception as e:
        print("error", e)
        return res(Errorapiresponse("011"))

# --- Calculate for NewTW/UsedTW ---
async def calculate_all(params: dict, res):
    try:
        nfa, localflatemi, localdeductionreceiveable = 0, 0, 0
        newpf, cdp, firstcdp = 0, 0, 0
        onroadprice = float(params["onroadprice"])
        advanceemi = float(params["advanceemi"])
        stampduty = float(params["stampduty"])
        rate = float(params["rate"])
        tenure = int(params["tenure"])
        processingfee = float(params["processingfee"])
        downpayment = float(params["downpayment"])
        emitype = params["emitype"]
        totaldeductiondecutible = float(params["totaldeductiondecutible"])
        totaldeductionreceiveable = float(params["totaldeductionreceiveable"])
        slabid = int(params["slabid"])

        if emitype == "rate":
            nfa = (onroadprice - downpayment + totaldeductiondecutible + stampduty)
            nfa += (processingfee * nfa * 0.01)
            newpf = (nfa * processingfee) / 100
            localflatemi = flat_emi(nfa, rate, tenure)
            firstcdp = onroadprice - nfa + newpf + stampduty + localflatemi * advanceemi

            i = 0
            while True:
                if i > 0:
                    firstcdp = cdp
                newpf = (nfa * processingfee) / 100
                localflatemi = flat_emi(nfa, rate, tenure)
                cdp = onroadprice - nfa + newpf + stampduty + localflatemi * advanceemi
                nfa = nfa + cdp - downpayment + totaldeductiondecutible
                if abs(firstcdp - cdp) < 0.00001 and i > 0:
                    break
                i += 1

        elif emitype == "flat":
            newpf = processingfee
            nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty + newpf

        elif emitype == "hybrid":
            nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty
            if slabid != 0:
                newpf = await calculate_hybrid_pf(slabid, nfa, res)
                i = 0
                while True:
                    newpf1 = await calculate_hybrid_pf(slabid, nfa + newpf, res)
                    if newpf == newpf1:
                        break
                    newpf = newpf1
                    i += 1
                nfa += newpf
        else:
            return res(Errorapiresponse("009"))

        if advanceemi == 0:
            localdeductionreceiveable = stampduty + newpf + totaldeductionreceiveable
            if rate and tenure:
                localflatemi = flat_emi(nfa, rate, tenure)
        else:
            localflatemi = flat_emi(nfa, rate, tenure)
            if emitype == "hybrid":
                firstpf = await calculate_hybrid_pf(slabid, nfa, res)
            elif emitype == "rate":
                firstpf = round((nfa * processingfee) / 100)
            else:
                firstpf = processingfee
            localdeductionreceiveable = (
                stampduty + firstpf + round(localflatemi) * advanceemi + totaldeductionreceiveable
            )
            i = 0
            firstemi = flat_emi(nfa, rate, tenure)
            while True:
                if i > 0:
                    firstemi = localflatemi
                localdeductionreceiveable = (
                    stampduty + newpf + round(localflatemi) * advanceemi
                )
                if rate and tenure:
                    nfa = onroadprice + localdeductionreceiveable - downpayment + totaldeductiondecutible
                    if emitype == "hybrid":
                        newpf = await calculate_hybrid_pf(slabid, nfa, res)
                    elif emitype == "rate":
                        newpf = (nfa * processingfee) / 100
                    else:
                        newpf = processingfee
                    localflatemi = flat_emi(nfa, rate, tenure)
                    if round(localflatemi) == round(firstemi):
                        break
                    i += 1

        return {
            "nfa": round(nfa),
            "newpf": round(newpf),
            "localflatemi": round(localflatemi),
            "localdeductionreceiveable": round(localdeductionreceiveable)
        }

    except Exception as e:
        print("Error in calculate_all:", e)
        return res(Errorapiresponse("012"))

# --- Calculate for RFV ---
async def calculate_all_rfv(params: dict, res):
    try:
        nfa, localflatemi, localdeductionreceiveable = 0, 0, 0
        onroadprice = float(params["onroadprice"])
        advanceemi = float(params["advanceemi"])
        stampduty = float(params["stampduty"])
        rate = float(params["rate"])
        tenure = int(params["tenure"])
        processingfee = float(params["processingfee"])
        emitype = params["emitype"]
        totaldeductiondecutible = float(params["totaldeductiondecutible"])
        totaldeductionreceiveable = float(params["totaldeductionreceiveable"])
        slabid = int(params["slabid"])

        if emitype == "rate":
            nfa = onroadprice + totaldeductiondecutible
            i = 0
            while True:
                newpf = round((nfa * processingfee) / 100)
                llemi = round(flat_emi(nfa, rate, tenure))
                cnfa = onroadprice + totaldeductiondecutible + llemi * advanceemi
                newpf = round((cnfa * processingfee) / 100)
                if round(nfa) == round(cnfa):
                    break
                nfa = cnfa
                i += 1

        elif emitype == "flat":
            newpf = processingfee
            nfa = onroadprice + totaldeductiondecutible

        elif emitype == "hybrid":
            nfa = onroadprice + totaldeductiondecutible
            if slabid != 0:
                newpf = await calculate_hybrid_pf(slabid, nfa, res)
                i = 0
                while True:
                    newpf1 = await calculate_hybrid_pf(slabid, nfa + newpf, res)
                    if newpf == newpf1:
                        break
                    newpf = newpf1
                    i += 1
        else:
            return res(Errorapiresponse("010"))

        if advanceemi == 0:
            localdeductionreceiveable = stampduty + newpf + totaldeductionreceiveable
            if rate and tenure:
                localflatemi = flat_emi(nfa, rate, tenure)
        else:
            localflatemi = flat_emi(nfa, rate, tenure)
            if emitype == "hybrid":
                firstpf = await calculate_hybrid_pf(slabid, nfa, res)
            elif emitype == "rate":
                firstpf = round((nfa * processingfee) / 100)
            else:
                firstpf = processingfee

            localdeductionreceiveable = (
                round(localflatemi) * advanceemi + stampduty + firstpf + totaldeductionreceiveable
            )
            i = 0
            firstemi = flat_emi(nfa, rate, tenure)
            while True:
                if i > 0:
                    firstemi = localflatemi
                localdeductionreceiveable = (
                    stampduty + newpf + round(localflatemi) * advanceemi + totaldeductionreceiveable
                )
                if rate and tenure:
                    nfa = onroadprice + totaldeductiondecutible + round(localflatemi) * advanceemi
                    if emitype == "hybrid":
                        newpf = await calculate_hybrid_pf(slabid, nfa, res)
                    elif emitype == "rate":
                        newpf = round((nfa * processingfee) / 100)
                    else:
                        newpf = processingfee
                    localflatemi = flat_emi(nfa, rate, tenure)
                    if round(localflatemi) == round(firstemi):
                        break
                    i += 1

        return {
            "nfa": round(nfa),
            "newpf": round(newpf),
            "localflatemi": round(localflatemi),
            "localdeductionreceiveable": round(localdeductionreceiveable)
        }

    except Exception as e:
        print("Error in calculate_all_rfv:", e)
        return res(Errorapiresponse("012"))
