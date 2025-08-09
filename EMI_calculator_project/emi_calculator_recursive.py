import os
import math
import httpx
from fastapi import APIRouter
from utils import Errorapiresponse

router = APIRouter()

# -------------------------------------------------------------------
# flatemi function
# input: {
#   p => principal
#   r => annualised rate of interest ROI()
#   t => tenure in month
# }
# output {
#   localflatemi => emi
# }
# -------------------------------------------------------------------
def flatemi(p, r, t):
    return (p + (p * (r / 100) * t) / 12) / t


# -------------------------------------------------------------------
# getpremium function
# input: {
#   tenure => annualised rate of interest ROI()
#   nfa => net finance amount
# }
# output {
#   premiumamount => premium Amount
# }
# -------------------------------------------------------------------
def getpremium(tenure, nfa):
    if nfa < 5000 or nfa > 200000:
        return 0
    if 0 < tenure <= 12:
        return nfa * 0.004
    elif 12 < tenure <= 24:
        return nfa * 0.008
    elif 24 < tenure <= 36:
        return nfa * 0.014
    else:
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
# input: { dob => DOB }
# output: { Age => Age }
# -------------------------------------------------------------------
def calculateage(dob):
    dd, mm, yyyy = dob.split("/")
    from datetime import date
    t1 = date.today()
    t2 = date(int(yyyy), int(mm), int(dd))
    diff_days = (t1 - t2).days
    return int(diff_days / 365)


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
# calculatehybridpf function (async)
# -------------------------------------------------------------------
async def calculatehybridpf(slabid, nfa, res):
    try:
        payload = {"Slab_Id": int(slabid), "Amount_Finacne": nfa}
        url = os.environ.get("u2w_process_fees")
        async with httpx.AsyncClient(timeout=10) as client:
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
# getstumpduty function (async)
# -------------------------------------------------------------------
async def getstumpduty(nfa, statecode, res):
    try:
        url = os.environ.get("stamp_duty_charge_api")
        payload = {"Amount_Finacne": nfa, "State_Code": statecode}
        async with httpx.AsyncClient(timeout=10) as client:
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
        print("error", e)
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

                if round(firstcdp) == round(cdp) and i > 0:
                    break
                i += 1

        elif emitype == "flat":
            newpf = processingfee
            nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty + processingfee

        elif emitype == "hybrid":
            nfa = onroadprice - downpayment + totaldeductiondecutible + stampduty
            if slabid != 0:
                newpf = await calculatehybridpf(slabid, nfa, res)
                newpf1 = await calculatehybridpf(slabid, nfa + newpf, res)
                i = 0
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

        if advanceemi == 0:
            localdeductionreceiveable = stampduty + newpf + totaldeductionreceiveable
            if rate and tenure:
                localflatemi = flatemi(nfa, rate, tenure)
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
# calculateallRFV function (RFV product) would follow here
# and the endpoint logic, plus the standalone test harness
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# calculateallRFV function - exact Node.js port
# -------------------------------------------------------------------
async def calculateallRFV(onroadprice, advanceemi, stampduty, rate, tenure,
                           processingfee, emitype, totaldeductiondecutible,
                           totaldeductionreceiveable, slabid, res):

    try:
        nfa = 0
        newpf = 0
        localflatemi = 0
        localdeductionreceiveable = 0

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
                if round(nfa) == round(cnfa):
                    break
                i += 1

        elif emitype == "flat":
            newpf = processingfee
            nfa = onroadprice + totaldeductiondecutible

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

        if advanceemi == 0:
            localdeductionreceiveable = stampduty + newpf + totaldeductionreceiveable
            if rate and tenure:
                localflatemi = flatemi(nfa, rate, tenure)
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
# FastAPI endpoint - calculate-emi
# -------------------------------------------------------------------
@router.post("/calculate-emi")
async def calculate_emi_endpoint(payload: dict):
    try:
        res_handler = lambda err: err

        # Extract params
        statecode = payload["statecode"]
        onroadprice = float(payload["onroadprice"])
        loanservicingcharge = float(payload["loanservicingcharge"])
        processingfee = float(payload["processingfee"])
        rate = float(payload["ROI"])
        advanceemi = float(payload["advanceemi"])
        tenure = int(payload["tenure"])
        downpayment = float(payload.get("downpayment", 0))
        emitype = payload["PF_Type"]
        managerincentive = float(payload["managerincentive"])
        subventioncharge = float(payload["subventioncharge"])
        documentationcharge = float(payload.get("documentationcharge", payload.get("documantationcharge", 0)))
        vechicleinsurancebywemi = float(payload["vechicleinsurancebywemi"])
        rtobywemi = float(payload["rtobywemi"])
        DCC = float(payload["DCC"])
        CPA_RTO_Penalty = float(payload["CPA_RTO_Penalty"])
        NACH = float(payload["NACH"])
        otherscharges = float(payload["otherscharges"])
        SEORP = float(payload["SEORP"])
        permisiibleLTV = float(payload["permisiibleLTV"])
        slabid = int(payload.get("slabid", 0))
        holdfornov = float(payload["holdfornoc"])
        holdfordrc = float(payload["holdfordrc"])
        fcamount = float(payload["fcamount"])
        riskpoolcharge = float(payload["riskpoolcharge"])
        dob = payload.get("dob")
        insurance = payload.get("LI_insurance")
        PA = payload.get("PA")
        Product_Id = int(payload["Product_Id"])

        # Determine product
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

        # Stamp duty
        totalcharge = DCC + NACH + otherscharges + documentationcharge
        totaldeductionreceiveable = managerincentive + subventioncharge

        localAmountFinancewithoutdeductions = onroadprice - downpayment
        if localAmountFinancewithoutdeductions <= 0:
            return Errorapiresponse("004")

        filterstump = await getstumpduty(localAmountFinancewithoutdeductions, statecode, res_handler)
        if not filterstump or not isinstance(filterstump, list):
            return Errorapiresponse("005")

        stampduty = filterstump[0]["stumpdutyamount"] + totalcharge + 32

        # Total deduction deductible
        totaldeductiondecutible = loanservicingcharge + vechicleinsurancebywemi + rtobywemi

        # First EMI calculation (without LI / PA)
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

        # ----------------------------
        # LI / PA Stabilization Loop
        # ----------------------------
        if insurance == "Y" or PA == "Y":
            age = calculateage(dob) if dob else 0
            if 18 <= age <= 60:
                previous_nfa = None
                while True:
                    if previous_nfa is not None and round(previous_nfa) == round(result["nfa"]):
                        break
                    previous_nfa = result["nfa"]

                    PAAmount = 0
                    Premium = 0

                    if PA == "Y":
                        PAAmount = get_pa_amount(tenure)

                    result["nfa"] += PAAmount

                    if insurance == "Y":
                        Premium = math.ceil(getpremium(tenure, result["nfa"]))

                    totaldeductiondecutible = (
                        loanservicingcharge +
                        Premium +
                        PAAmount +
                        vechicleinsurancebywemi +
                        rtobywemi
                    )

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

                    result["Premium"] = Premium
                    result["PAAmount"] = PAAmount

        # Final LTV calculations
        LTV = ((result["nfa"] - result["localflatemi"] * advanceemi) / onroadprice) * 100
        SELTV = ((result["nfa"] - result["localflatemi"] * advanceemi) / SEORP) * 100

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

# -------------------------------------------------------------------
# Standalone test harness
# -------------------------------------------------------------------
if __name__ == "__main__":
    import asyncio
    async def test():
        payload = {
            "statecode": 1,
            "onroadprice": 50000,
            "loanservicingcharge": 1000,
            "processingfee": 2,
            "ROI": 10,
            "advanceemi": 1,
            "tenure": 12,
            "downpayment": 5000,
            "PF_Type": "rate",
            "managerincentive": 0,
            "subventioncharge": 0,
            "documentationcharge": 0,
            "vechicleinsurancebywemi": 0,
            "rtobywemi": 0,
            "DCC": 0,
            "CPA_RTO_Penalty": 0,
            "NACH": 0,
            "otherscharges": 0,
            "SEORP": 50000,
            "permisiibleLTV": 80,
            "slabid": 0,
            "holdfornoc": 0,
            "holdfordrc": 0,
            "fcamount": 0,
            "riskpoolcharge": 0,
            "dob": "01/01/1990",
            "LI_insurance": "N",
            "PA": "N",
            "Product_Id": 5000383
        }
        result = await calculate_emi_endpoint(payload)
        print(result)
    asyncio.run(test())
