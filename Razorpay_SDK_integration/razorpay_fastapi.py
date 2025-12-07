"""
razorpay_fastapi.py

Requirements:
    pip install razorpay fastapi uvicorn python-dotenv

Run (dev):
    export RZP_KEY_ID=your_test_key_id
    export RZP_KEY_SECRET=your_test_key_secret
    export RZP_WEBHOOK_SECRET=your_webhook_secret   # optional but recommended
    uvicorn razorpay_fastapi:app --reload --port 8000

This app exposes:
 - POST /create_order       -> create an order
 - POST /capture_payment    -> capture a payment (manual capture)
 - POST /refund             -> refund a payment (full or partial)
 - POST /webhook            -> webhook endpoint (verifies signature)
 - GET  /health             -> simple health check
"""

import os
from decimal import Decimal, InvalidOperation
from typing import Optional

import razorpay
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

RZP_KEY_ID = os.getenv("RZP_KEY_ID")
RZP_KEY_SECRET = os.getenv("RZP_KEY_SECRET")
RZP_WEBHOOK_SECRET = os.getenv("RZP_WEBHOOK_SECRET", "")

if not (RZP_KEY_ID and RZP_KEY_SECRET):
    raise RuntimeError("Set RZP_KEY_ID and RZP_KEY_SECRET environment variables")

# Initialize client once
client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

app = FastAPI(title="Razorpay FastAPI Demo")


# ---------------------
# Pydantic request models
# ---------------------
class CreateOrderReq(BaseModel):
    amount: Decimal = Field(..., description="Amount in rupees. Example: 100.50")
    currency: Optional[str] = Field("INR")
    receipt: Optional[str] = Field(None)
    payment_capture: Optional[int] = Field(0, description="0 = manual capture, 1 = auto-capture")


class CapturePaymentReq(BaseModel):
    payment_id: str
    amount: Decimal = Field(..., description="Amount in rupees to capture (must match subunits)")


class RefundReq(BaseModel):
    payment_id: str
    amount: Optional[Decimal] = Field(None, description="Optional partial refund amount in rupees. Omit for full refund.")


# ---------------------
# Helpers
# ---------------------
def to_subunits(amount_rupees) -> int:
    """
    Convert rupees (Decimal/str/float) to integer paise.
    Keeps safe rounding by converting through Decimal.
    """
    try:
        amt = Decimal(str(amount_rupees))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid amount")
    # Multiply by 100 and quantize to whole paise
    sub = int((amt * 100).quantize(Decimal("1")))
    if sub < 0:
        raise ValueError("Amount must be non-negative")
    return sub


def razorpay_error_to_http(e: Exception) -> HTTPException:
    # keep it simple: map to 502 / 400 depending on exception type
    return HTTPException(status_code=502, detail=f"Razorpay error: {e}")


# ---------------------
# Endpoints
# ---------------------
@app.post("/create_order")
async def create_order(req: CreateOrderReq):
    """
    Create an order.
    Request JSON:
      { "amount": 100.50, "currency": "INR", "receipt": "rcpt_1", "payment_capture": 0 }
    Response: raw order object from Razorpay
    """
    try:
        amount_subunits = to_subunits(req.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    payload = {
        "amount": amount_subunits,
        "currency": req.currency or "INR",
        "receipt": req.receipt or f"rcpt_{os.urandom(4).hex()}",
        "payment_capture": int(req.payment_capture or 0),
    }
    try:
        order = client.order.create(data=payload)
        return JSONResponse(content=order)
    except Exception as e:
        raise razorpay_error_to_http(e)


@app.post("/capture_payment")
async def capture_payment(req: CapturePaymentReq):
    """
    Capture a payment (manual capture).
    Request JSON:
      { "payment_id": "pay_XXXX", "amount": 100.50 }
    """
    try:
        amount_subunits = to_subunits(req.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = client.payment.capture(req.payment_id, amount_subunits)
        return JSONResponse(content=result)
    except Exception as e:
        raise razorpay_error_to_http(e)


@app.post("/refund")
async def refund(req: RefundReq):
    """
    Refund a payment. Omit amount for full refund.
    Request JSON:
      { "payment_id": "pay_XXXX", "amount": 50.00 }  # partial refund
      or
      { "payment_id": "pay_XXXX" }  # full refund
    """
    payload = {}
    if req.amount is not None:
        try:
            payload["amount"] = to_subunits(req.amount)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    try:
        result = client.payment.refund(req.payment_id, payload)
        return JSONResponse(content=result)
    except Exception as e:
        raise razorpay_error_to_http(e)


@app.post("/webhook")
async def webhook(request: Request, x_razorpay_signature: Optional[str] = Header(None)):
    """
    Webhook endpoint. Verify signature BEFORE parsing JSON.
    Razorpay sends header: X-Razorpay-Signature
    Use raw body for verification.
    """
    if not RZP_WEBHOOK_SECRET:
        # Fail safe: require server-side config of webhook secret
        raise HTTPException(status_code=500, detail="Webhook secret not configured on server")

    raw_body = await request.body()  # bytes
    signature = x_razorpay_signature or request.headers.get("X-Razorpay-Signature", "")

    try:
        # SDK expects string body (or bytes in some versions). Use decoded string.
        client.utility.verify_webhook_signature(raw_body.decode("utf-8"), signature, RZP_WEBHOOK_SECRET)
    except Exception:
        # signature invalid -> 400
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Safe to parse JSON after verification
    payload = await request.json()
    event = payload.get("event")
    # TODO: process event (example: record order/payment status in DB)
    # IMPORTANT: ensure idempotency when processing events (use payload['payload']['payment']['entity']['id'] or X-Razorpay-Event-Id if you log it)
    return JSONResponse(content={"status": "ok", "event": event})


@app.get("/health")
async def health():
    return {"status": "ok"}


# ---------------------
# Notes printed when run directly (optional)
# ---------------------
if __name__ == "__main__":
    import uvicorn

    print("Razorpay FastAPI demo starting on http://0.0.0.0:8000")
    uvicorn.run("razorpay_fastapi:app", host="0.0.0.0", port=8000, reload=True)