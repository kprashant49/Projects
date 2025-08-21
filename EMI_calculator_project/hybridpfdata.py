"""
hybridpfdata.py
Local dataset and lookup for Hybrid Processing Fees.

Mimics the external API response so that emi_calculator.py
can consume it without code changes.
"""

from typing import Dict, Union

# -------------------------------------------------------------------
# Hybrid PF table
# -------------------------------------------------------------------
hybrid_pf_table = [
    {'Slab_Id': 1, 'Min_Charge_Amt': 1500, 'Max_Charge_Amt': 2500, 'Multiplier': 1.5},
    {'Slab_Id': 2, 'Min_Charge_Amt': 1500, 'Max_Charge_Amt': 2500, 'Multiplier': 1.5},
    {'Slab_Id': 3, 'Min_Charge_Amt': 500,  'Max_Charge_Amt': 1250, 'Multiplier': 0.5},
    {'Slab_Id': 4, 'Min_Charge_Amt': 500,  'Max_Charge_Amt': 1500, 'Multiplier': 0.5},
    {'Slab_Id': 5, 'Min_Charge_Amt': 1000, 'Max_Charge_Amt': 1000, 'Multiplier': 1.0},
    {'Slab_Id': 6, 'Min_Charge_Amt': 1000, 'Max_Charge_Amt': 1250, 'Multiplier': 1.0},
    {'Slab_Id': 7, 'Min_Charge_Amt': 1000, 'Max_Charge_Amt': 1500, 'Multiplier': 1.0},
    {'Slab_Id': 8, 'Min_Charge_Amt': 1000, 'Max_Charge_Amt': 6000, 'Multiplier': 1.0},
    {'Slab_Id': 9, 'Min_Charge_Amt': 500,  'Max_Charge_Amt': 2000, 'Multiplier': 0.5},
    {'Slab_Id': 10, 'Min_Charge_Amt': 500, 'Max_Charge_Amt': 600,  'Multiplier': 0.5}
]


# -------------------------------------------------------------------
# get_hybrid_pf function (mimics API)
# -------------------------------------------------------------------
def get_hybrid_pf(slab_id: int, amount_finance: float) -> Dict[str, Union[bool, Dict[str, Union[int, float]]]]:
    """
    Calculate Hybrid Processing Fee based on local table.

    Args:
        slab_id (int): Slab identifier.
        amount_finance (float): Finance amount.

    Returns:
        dict: API-like response
              {
                  "Success": True/False,
                  "Message": {
                      "Min_Charge_Amt": int,
                      "Max_Charge_Amt": int,
                      "Processing_Fees": int
                  }
              }
    """
    # Lookup slab
    slab = next((s for s in hybrid_pf_table if s["Slab_Id"] == slab_id), None)
    if not slab:
        return {"Success": False, "Message": {"Error": f"Slab_Id {slab_id} not found"}}

    min_amt = slab["Min_Charge_Amt"]
    max_amt = slab["Max_Charge_Amt"]
    multiplier = slab["Multiplier"]

    # Calculate processing fee
    calculated_fee = amount_finance * (multiplier / 100.0)

    # Apply min/max rules
    if calculated_fee < min_amt:
        fee = min_amt
    elif calculated_fee > max_amt:
        fee = max_amt
    else:
        fee = calculated_fee

    return {
        "Success": True,
        "Message": {
            "Min_Charge_Amt": min_amt,
            "Max_Charge_Amt": max_amt,
            "Processing_Fees": int(round(fee)),
        },
    }
