# streamlit_razorpay_frontend.py
# Requirements:
#   pip install streamlit requests
#
# Run:
#   streamlit run streamlit_razorpay_frontend.py

import os
import json
import requests
import streamlit as st
from decimal import Decimal, InvalidOperation

st.set_page_config(page_title="Razorpay Streamlit Demo", layout="centered")

st.title("Razorpay Streamlit Frontend (Demo)")

# --- Config ---
st.markdown(
    "This frontend talks to your FastAPI server (default `http://localhost:8000`). "
    "It uses your **Razorpay Key ID** (public) to open Checkout. "
    "Keep your secret key on server-side only."
)

col1, col2 = st.columns(2)
with col1:
    api_base = st.text_input("FastAPI Base URL", value=os.getenv("API_BASE", "http://localhost:8000"))
with col2:
    RZP_KEY_ID = st.text_input("Razorpay Key ID (public)", value=os.getenv("RZP_KEY_ID", ""))

st.write("---")

# Helper: convert rupees -> paise
def to_subunits(amount):
    try:
        amt = Decimal(str(amount))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid amount")
    sub = int((amt * 100).quantize(Decimal("1")))
    if sub <= 0:
        raise ValueError("Amount must be > 0")
    return sub

# -------------------------
# Section: Create Order + Checkout
# -------------------------
st.header("1) Create order & Open Checkout")

with st.form("create_order_form"):
    rupees = st.text_input("Amount (INR)", value="100.00")
    receipt = st.text_input("Receipt (optional)", value="")
    payment_capture = st.selectbox("Payment capture mode", options=[0, 1], index=0, help="0 = manual capture, 1 = auto-capture")
    name = st.text_input("Merchant name (shown in checkout)", value="My Demo Store")
    description = st.text_input("Description (checkout)", value="Test payment")
    email = st.text_input("Customer email (prefill)", value="")
    phone = st.text_input("Customer phone (prefill)", value="")
    submitted = st.form_submit_button("Create Order & Open Checkout")

if submitted:
    # Validate
    if not RZP_KEY_ID:
        st.error("Enter Razorpay Key ID (public).")
    else:
        try:
            subunits = to_subunits(rupees)
        except Exception as e:
            st.error(f"Invalid amount: {e}")
            st.stop()

        payload = {
            "amount": float(rupees),  # our FastAPI expects rupees (it will convert)
            "currency": "INR",
            "receipt": receipt or None,
            "payment_capture": int(payment_capture),
        }
        try:
            resp = requests.post(f"{api_base.rstrip('/')}/create_order", json=payload, timeout=10)
            resp.raise_for_status()
            order = resp.json()
        except Exception as e:
            st.error(f"Failed to create order via API ({api_base}): {e}")
            st.stop()

        st.success("Order created on server.")
        st.json(order)

        # Extract fields
        order_id = order.get("id")
        order_amount = order.get("amount", subunits)  # amount in paise
        currency = order.get("currency", "INR")

        if not order_id:
            st.error("Order created but response missing order['id']. Cannot open checkout.")
            st.stop()

        # Build Checkout HTML that opens Razorpay
        st.info("Opening Razorpay Checkout. After payment completes, copy the `payment_id` from the success alert and paste it into the Capture/Refund section below.")
        checkout_html = f"""
        <html>
          <head>
            <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
          </head>
          <body>
            <script>
              const options = {{
                "key": "{RZP_KEY_ID}",
                "amount": "{order_amount}", // in paise
                "currency": "{currency}",
                "name": "{name}",
                "description": "{description}",
                "order_id": "{order_id}",
                "handler": function (response) {{
                  // Show result as alert so user can copy payment_id
                  alert("Payment successful!\\n" +
                        "payment_id: " + response.razorpay_payment_id + "\\n" +
                        "order_id: " + response.razorpay_order_id + "\\n" +
                        "signature: " + response.razorpay_signature);
                }},
                "modal": {{
                  "ondismiss": function() {{
                    // Notify user to check if payment went through
                    console.log("Checkout closed without payment");
                  }}
                }},
                "prefill": {{
                  "email": "{email}",
                  "contact": "{phone}"
                }},
                "theme": {{
                  "color": "#3399cc"
                }}
              }};
              const rzp = new Razorpay(options);
              // Open checkout after a short delay to allow the component to mount
              setTimeout(()=> rzp.open(), 200);
            </script>
            <p>If checkout didn't open automatically, <button onclick="rzp.open()">Open Checkout</button></p>
          </body>
        </html>
        """

        # Embed the HTML (allow scripts)
        st.components.v1.html(checkout_html, height=650, scrolling=True)

st.write("---")

# -------------------------
# Section: Capture payment
# -------------------------
st.header("2) Capture payment (manual capture mode only)")

with st.form("capture_form"):
    capture_payment_id = st.text_input("Payment ID to capture (paste from checkout success alert)", value="")
    capture_amount = st.text_input("Amount to capture (INR, must match original)", value="")
    capture_submitted = st.form_submit_button("Capture Payment")

if capture_submitted:
    if not capture_payment_id:
        st.error("Enter payment_id to capture.")
    else:
        try:
            _ = to_subunits(capture_amount)
        except Exception as e:
            st.error(f"Invalid amount: {e}")
            st.stop()
        payload = {"payment_id": capture_payment_id, "amount": float(capture_amount)}
        try:
            resp = requests.post(f"{api_base.rstrip('/')}/capture_payment", json=payload, timeout=10)
            resp.raise_for_status()
            st.success("Capture successful.")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Capture failed: {e}")

st.write("---")

# -------------------------
# Section: Refund
# -------------------------
st.header("3) Refund (full or partial)")

with st.form("refund_form"):
    refund_payment_id = st.text_input("Payment ID to refund", value="")
    refund_amount = st.text_input("Refund amount (INR, optional for partial)", value="")
    refund_submitted = st.form_submit_button("Refund")

if refund_submitted:
    if not refund_payment_id:
        st.error("Enter payment_id to refund.")
    else:
        payload = {"payment_id": refund_payment_id}
        if refund_amount.strip():
            try:
                _ = to_subunits(refund_amount)
            except Exception as e:
                st.error(f"Invalid amount: {e}")
                st.stop()
            payload["amount"] = float(refund_amount)
        try:
            resp = requests.post(f"{api_base.rstrip('/')}/refund", json=payload, timeout=10)
            resp.raise_for_status()
            st.success("Refund initiated.")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Refund failed: {e}")

st.write("---")
st.markdown(
    """
**Notes**
- Use Razorpay *test* key pair on server for development. Never expose secret keys in this frontend.
- This demo expects your FastAPI server to implement `/create_order`, `/capture_payment`, `/refund` compatible with the payloads the frontend sends (amount in rupees).
- After successful checkout, the JS handler shows an alert with `payment_id`. Copy & paste that into the Capture/Refund sections above.
"""
)