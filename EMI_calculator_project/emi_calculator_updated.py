# emi_calculator.py
import os
import math
import httpx
from fastapi import APIRouter
from utils import Errorapiresponse

router = APIRouter()

# -------------------------------------------------------------------
# flatemi function
# input:{
# p=>principal
#      r=> annualised rate of interest ROI()
#      t=> tenure in month}
# output{
# localflatemi=>emi
# }
# -------------------------------------------------------------------
def flatemi(p, r, t):
    return (p + (p * (r / 100) * t) / 12) / t

# -------------------------------------------------------------------
# getpremium function
# input:{
#      tenure=> months
#      nfa => net finance amount
# output{
# premiumamount=>premium Amount
# }
# -------------------------------------------------------------------
def getpremium(tenure, nfa):
    try:
        if nfa < 5000 or nfa > 200000:
            return 0
        if tenure > 0 and tenure <= 12:
            return nfa * 0.004
        elif tenure > 12 and tenure <= 24:
            return nfa * 0.008
        elif tenure > 24 and tenure <= 36:
            return nfa * 0.014
        else:
            return 0
    except Exception as e:
        print("getpremium error:", e)
        return 0

# -------------------------------------------------------------------
# get_pa_amount function
# -------------------------------------------------------------------
def get_pa_amount(tenure):
    if tenure <= 12:
        return 719
    elif 12 < tenure <= 24:
        return 371
    elif 24 < tenure <= 36:
        return 399
    else:
        return 0

# -------------------------------------------------------------------
# calculateage function
# input:{ dob=> DOB }
# output:{ Age=>Age }
# -------------------------------------------------------------------
def calculateage(dob):
    # dob expected format DD/MM/YYYY
    dd, mm, yyyy = dob.split("/")
    from datetime import date
    t1 = date.today()
    t2 = date(int(yyyy), int(mm), int(dd))
    diff_days = (t1 - t2).days
    age = diff_days / 365
    return int(str(age).split(".")[0])

# -------------------------------------------------------------------
# isnumberfun function
# -------------------------------------------------------------------
def isnumberfun(arr):
    errorstring = "Please send correct number Input for"
    for k, v in arr.items():
        try:
            float(v)
        except:
            errorstring += f" {k},"
    return errorstring[:-1]

# -------------------------------------------------------------------
# calculatehybridpf function (async) - calls the PF API
# -------------------------------------------------------------------
async def calculatehybridpf(slabid, nfa, res):
    try:
        payload = {"Slab_Id": int(slabid), "Amount_Finacne": nfa}
        url = os.environ.get("u2w_process_fees")
        async with httpx.AsyncClient(timeout=15) as client:
            slabres = await client.post(url, json=payload)
        data = slabres.json()
        print("hybridres", data)
        if data.get("Success"):
            return data["Message"]["Processing_Fees"]
        else:
            return res(Errorapiresponse("006"))
    except Exception as e:
        print("calculatehybridpf error:", e)
        return res(Errorapiresponse("012"))

# -------------------------------------------------------------------
# getstumpduty function (async) - calls stamp duty API once per request
# -------------------------------------------------------------------
async def getstumpduty(nfa, statecode, res):
    try:
        url = os.environ.get("stamp_duty_charge_api")
        payload = {"Amount_Finacne": nfa, "State_Code": statecode}
        async with httpx.AsyncClient(timeout=15) as client:
            resstump = await client.post(url, json=payload)
        data = resstump.json()
        print("resstump", data)
        if data.get("Success"):
            if data["Message"].get("stamp_duty_charge") is not None:
                return [{"stumpdutyamount": data["Message"]["stamp_duty_charge"]}]
            else:
                return res(Errorapiresponse("011"))
        else:
            return res(Errorapiresponse("011"))
    except Exception as e:
        print("getstumpduty error:", e)
        return res(Errorapiresponse("011"))

# -------------------------------------------------------------------
# calculateall function (NewTW/UsedTW) - exact Node.js port
# -------------------------------------------------------------------
async def calculateall(onroadprice, advanceemi, stampduty, rate, tenure,
                        processingfee, downpayment, emitype,
                        totaldeductiondecutible, totaldeductionreceiveable,
                        slabid, res):

    try:
        nfa = 0
        newpf = 0
        localflatemi = 0
        localdeductionreceiveable = 0

        # ------------------ emitype == "rate" branch ------------------
        if emitype == "rate":
            nfa = (onroadprice - downpayment +
                   totaldeductiondecutible + stampduty +
                   0.01 * processingfee * (onroadprice - downpayment +
                   totaldeductiondecutible + stampduty))

            newpf = (nfa * processingfee) / 100

            llemi = round(flatemi(nfa, rate, tenure))

            firstcdp = (onroadprice - nfa + newpf + stampduty +
                        (llemi * advanceemi))

            i = 0
            while True:
                if i > 0:
                    firstcdp = cdp

                newpf = (nfa * processingfee) / 100
                llemi = round(flatemi(nfa, rate, tenure))
                cdp = (onroadprice - nfa + newpf + stampduty +
                       (llemi * advanceemi))
                nfa = nfa + cdp - downpayment + totaldeductiondecutible
                newpf = (nfa * processingfee) / 100

                # match JS: break when Math.round(firstcdp) == Math.round(cdp)
                if round(firstcdp) == round(cdp) and i > 0:
                    break
                i += 1

        # ------------------ emitype == "flat" branch ------------------
        elif emitype == "flat":
            newpf = processingfee
            nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty + processingfee

        # ------------------ emitype == "hybrid" branch ------------------
        elif emitype == "hybrid":
            nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty
            if slabid != 0:
                newpf = await calculatehybridpf(slabid, nfa, res)
                # PF stabilization loop (call PF API until it stabilizes)
                i = 0
                newpf1 = await calculatehybridpf(slabid, nfa + newpf, res)
                while True:
                    if i > 0:
                        newpf = newpf1
                    newpf1 = await calculatehybridpf(slabid, nfa + newpf, res)
                    print("iteration==>", i, "pf==>", newpf)
                    if round(newpf) == round(newpf1):
                        break
                    i += 1
                nfa = nfa + newpf
        else:
            return res(Errorapiresponse("009"))

        # ------------------ advanceemi == 0 branch ------------------
        if advanceemi == 0:
            localdeductionreceiveable = stampduty + newpf + totaldeductionreceiveable
            if rate and tenure:
                localflatemi = flatemi(nfa, rate, tenure)

        # ------------------ advanceemi > 0 branch ------------------
        else:
            localflatemi = flatemi(nfa, rate, tenure)

            if emitype == "hybrid":
                firstpf = await calculatehybridpf(slabid, nfa, res)
            elif emitype == "rate":
                newpf = (nfa * processingfee) / 100
            elif emitype == "flat":
                newpf = processingfee

            localdeductionreceiveable = (stampduty + (firstpf if emitype == "hybrid" else newpf) +
                                         round(localflatemi) * advanceemi +
                                         totaldeductionreceiveable)

            firstemi = flatemi(nfa, rate, tenure)
            i = 0
            while True:
                if i > 0:
                    firstemi = localflatemi

                localdeductionreceiveable = (stampduty + newpf +
                                             round(localflatemi) * advanceemi)

                if rate and tenure:
                    nfa = (onroadprice + localdeductionreceiveable -
                           downpayment + totaldeductiondecutible)

                    if emitype == "hybrid":
                        newpf = await calculatehybridpf(slabid, nfa, res)
                    elif emitype == "rate":
                        newpf = (nfa * processingfee) / 100
                    elif emitype == "flat":
                        newpf = processingfee

                    localflatemi = flatemi(nfa, rate, tenure)

                    print("iteration=>", i, "emi=", localflatemi,
                          "nfa=", nfa, "pf", newpf)

                    # match JS: break when Math.round(localflatemi) == Math.round(firstemi)
                    if round(localflatemi) == round(firstemi):
                        break
                    i += 1

        localflatemi = round(localflatemi)
        return {"nfa": nfa, "newpf": newpf,
                "localflatemi": localflatemi,
                "localdeductionreceiveable": localdeductionreceiveable}

    except Exception as e:
        print("calculateall error:", e)
        return res(Errorapiresponse("012"))

# -------------------------------------------------------------------
# calculateallRFV function (RFV product) - exact Node.js port
# -------------------------------------------------------------------
async def calculateallRFV(onroadprice, advanceemi, stampduty, rate, tenure,
                           processingfee, emitype, totaldeductiondecutible,
                           totaldeductionreceiveable, slabid, res):

    try:
        nfa = 0
        newpf = 0
        localflatemi = 0
        localdeductionreceiveable = 0

        # ------------------ emitype == "rate" branch ------------------
        if emitype == "rate":
            nfa = onroadprice + totaldeductiondecutible
            cnfa = nfa
            i = 0
            while True:
                if i > 0:
                    cnfa = nfa
                newpf = round((nfa * processingfee) / 100)
                llemi = round(flatemi(nfa, rate, tenure))
                nfa = onroadprice + totaldeductiondecutible + (llemi * advanceemi)
                newpf = round((nfa * processingfee) / 100)
                print("iteration", i, "nfa===>", nfa)
                # break when Math.round(nfa) == Math.round(cnfa)
                if round(nfa) == round(cnfa):
                    break
                i += 1

        # ------------------ emitype == "flat" branch ------------------
        elif emitype == "flat":
            newpf = processingfee
            nfa = onroadprice + totaldeductiondecutible

        # ------------------ emitype == "hybrid" branch ------------------
        elif emitype == "hybrid":
            nfa = onroadprice + totaldeductiondecutible
            if slabid != 0:
                newpf = await calculatehybridpf(slabid, nfa, res)
                i = 0
                while True:
                    newpf1 = await calculatehybridpf(slabid, nfa + newpf, res)
                    print("iteration==>", i, newpf1, newpf)
                    if round(newpf) == round(newpf1):
                        break
                    newpf = newpf1
                    i += 1

        else:
            return res(Errorapiresponse("010"))

        # ------------------ advanceemi == 0 branch ------------------
        if advanceemi == 0:
            localdeductionreceiveable = stampduty + newpf + totaldeductionreceiveable
            if rate and tenure:
                localflatemi = flatemi(nfa, rate, tenure)
        # ------------------ advanceemi > 0 branch ------------------
        else:
            localflatemi = flatemi(nfa, rate, tenure)
            if emitype == "hybrid":
                firstpf = await calculatehybridpf(slabid, nfa, res)
            elif emitype == "rate":
                newpf = round((nfa * processingfee) / 100)
            elif emitype == "flat":
                newpf = processingfee

            localdeductionreceiveable = (round(localflatemi) * advanceemi +
                                         stampduty + (firstpf if emitype == "hybrid" else newpf) +
                                         totaldeductionreceiveable)

            firstemi = flatemi(nfa, rate, tenure)
            i = 0
            while True:
                if i > 0:
                    firstemi = localflatemi
                localdeductionreceiveable = (stampduty + newpf +
                                             round(localflatemi) * advanceemi +
                                             totaldeductionreceiveable)
                if rate and tenure:
                    nfa = (onroadprice + totaldeductiondecutible +
                           round(localflatemi) * advanceemi)
                    if emitype == "hybrid":
                        newpf = await calculatehybridpf(slabid, nfa, res)
                    elif emitype == "rate":
                        newpf = round((nfa * processingfee) / 100)
                    elif emitype == "flat":
                        newpf = processingfee
                    localflatemi = flatemi(nfa, rate, tenure)
                    print("pf=====", i, newpf, nfa)
                    if round(localflatemi) == round(firstemi):
                        break
                i += 1

        localflatemi = round(localflatemi)
        return {"nfa": nfa, "newpf": newpf,
                "localflatemi": localflatemi,
                "localdeductionreceiveable": localdeductionreceiveable}

    except Exception as e:
        print("calculateallRFV error:", e)
        return res(Errorapiresponse("012"))

# -------------------------------------------------------------------
# calculate-emi endpoint - full flow including LI/PA stabilization loop
# -------------------------------------------------------------------
@router.post("/calculate-emi")
async def calculate_emi_endpoint(payload: dict):
    try:
        res_handler = lambda err: err  # returns whatever Errorapiresponse gives

        # ----------- Extract & normalize inputs -----------
        # Minimal defensive parsing; expect caller to pass valid numeric values
        statecode = payload.get("statecode")
        onroadprice = float(payload.get("onroadprice", 0))
        loanservicingcharge = float(payload.get("loanservicingcharge", 0))
        processingfee = float(payload.get("processingfee", 0))
        rate = float(payload.get("ROI", 0))
        advanceemi = float(payload.get("advanceemi", 0))
        tenure = int(payload.get("tenure", 0))
        downpayment = float(payload.get("downpayment", 0))
        emitype = payload.get("PF_Type")
        managerincentive = float(payload.get("managerincentive", 0))
        subventioncharge = float(payload.get("subventioncharge", 0))
        documentationcharge = float(payload.get("documentationcharge", payload.get("documantationcharge", 0)))
        vechicleinsurancebywemi = float(payload.get("vechicleinsurancebywemi", 0))
        rtobywemi = float(payload.get("rtobywemi", 0))
        DCC = float(payload.get("DCC", 0))
        CPA_RTO_Penalty = float(payload.get("CPA_RTO_Penalty", 0))
        NACH = float(payload.get("NACH", 0))
        otherscharges = float(payload.get("otherscharges", 0))
        SEORP = float(payload.get("SEORP", 0))
        permisiibleLTV = float(payload.get("permisiibleLTV", 0))
        slabid = int(payload.get("slabid", 0))
        holdfornov = float(payload.get("holdfornoc", 0))
        holdfordrc = float(payload.get("holdfordrc", 0))
        fcamount = float(payload.get("fcamount", 0))
        riskpoolcharge = float(payload.get("riskpoolcharge", 0))
        dob = payload.get("dob")
        insurance = payload.get("LI_insurance")
        PA = payload.get("PA")
        Product_Id = int(payload.get("Product_Id", 0))

        # ----------- Basic checks & product detection -----------
        if Product_Id == 5000462:
            product = "RFV"
        elif Product_Id in (5000383, 5000382):
            product = "NewTW"
        else:
            return Errorapiresponse("002")

        disbursementdeductions = (holdfornov + holdfordrc + fcamount +
                                  riskpoolcharge + CPA_RTO_Penalty)

        # Adjust onroadprice for certain products
        if Product_Id in (5000462, 5000382):
            onroadprice = onroadprice - rtobywemi - vechicleinsurancebywemi

        # Stamp duty & totalcharge
        totalcharge = DCC + NACH + otherscharges + documentationcharge
        totaldeductionreceiveable = managerincentive + subventioncharge

        localAmountFinancewithoutdeductions = onroadprice - downpayment
        if localAmountFinancewithoutdeductions <= 0:
            return Errorapiresponse("004")

        # Call stamp duty API once
        filterstump = await getstumpduty(localAmountFinancewithoutdeductions, statecode, res_handler)
        if not filterstump or not isinstance(filterstump, list):
            return Errorapiresponse("005")

        stampduty = filterstump[0]["stumpdutyamount"] + totalcharge + 32

        # total deduction deductible
        totaldeductiondecutible = loanservicingcharge + vechicleinsurancebywemi + rtobywemi

        # ----------- First EMI calculation (without LI / PA) -----------
        if product == "RFV":
            result = await calculateallRFV(
                onroadprice, advanceemi, stampduty, rate, tenure,
                processingfee, emitype, totaldeductiondecutible,
                totaldeductionreceiveable, slabid, res_handler
            )
        else:
            result = await calculateall(
                onroadprice, advanceemi, stampduty, rate, tenure,
                processingfee, downpayment, emitype,
                totaldeductiondecutible, totaldeductionreceiveable,
                slabid, res_handler
            )

        if not result or not result.get("newpf"):
            return Errorapiresponse("006")

        # -------------------------------------------------------------------
        # LI / PA Stabilization Loop (match Node.js behavior)
        # -------------------------------------------------------------------
        if insurance == "Y" or PA == "Y":
            age = calculateage(dob) if dob else 0
            if 18 <= age <= 60:
                previous_nfa = None
                # Loop until NFA stabilizes after adding PA & Premium
                while True:
                    if previous_nfa is not None and round(previous_nfa) == round(result["nfa"]):
                        break

                    previous_nfa = result["nfa"]

                    PAAmount = 0
                    Premium = 0

                    # PA
                    if PA == "Y":
                        PAAmount = get_pa_amount(tenure)

                    # Add PA (affects nfa)
                    result["nfa"] += PAAmount

                    # LI premium based on updated nfa
                    if insurance == "Y":
                        Premium = math.ceil(getpremium(tenure, result["nfa"]))

                    # Update totaldeductiondecutible with Premium/PA
                    totaldeductiondecutible = (
                        loanservicingcharge +
                        Premium +
                        PAAmount +
                        vechicleinsurancebywemi +
                        rtobywemi
                    )

                    # Re-run full calculation with updated deductions
                    if product == "RFV":
                        result = await calculateallRFV(
                            onroadprice, advanceemi, stampduty, rate, tenure,
                            processingfee, emitype, totaldeductiondecutible,
                            totaldeductionreceiveable, slabid, res_handler
                        )
                    else:
                        result = await calculateall(
                            onroadprice, advanceemi, stampduty, rate, tenure,
                            processingfee, downpayment, emitype,
                            totaldeductiondecutible, totaldeductionreceiveable,
                            slabid, res_handler
                        )

                    # Keep Premium & PAAmount in result for final message
                    result["Premium"] = Premium
                    result["PAAmount"] = PAAmount

        # ----------- Final LTV calculations & response -----------
        LTV = ((result["nfa"] - result["localflatemi"] * advanceemi) / onroadprice) * 100 if onroadprice else 0
        SELTV = ((result["nfa"] - result["localflatemi"] * advanceemi) / SEORP) * 100 if SEORP else 0

        return {
            "Success": True,
            "Message": {
                "flatemi": round(result["localflatemi"]),
                "Net_Finance_amount": round(result["nfa"]),
                "deduction": round(result["localdeductionreceiveable"]),
                "stampduty": filterstump[0]["stumpdutyamount"],
                "stampdutyservicecharge": 32,
                "processingfee": round(result["newpf"]),
                "Premium": result.get("Premium", 0),
                "PAAmount": result.get("PAAmount", 0),
                "LTV": round(LTV, 2),
                "SELTV": round(SELTV, 2)
            }
        }

    except Exception as e:
        print("API error:", e)
        return Errorapiresponse("012")