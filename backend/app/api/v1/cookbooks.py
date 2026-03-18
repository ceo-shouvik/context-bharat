"""Integration cookbooks — pre-built multi-API integration guides."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cookbooks", tags=["cookbooks"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class CookbookStep(BaseModel):
    step_number: int
    title: str
    description: str
    api: str
    code: str
    language: str = "python"


class CookbookSummary(BaseModel):
    id: str
    title: str
    description: str
    apis_used: list[str]
    difficulty: str = "intermediate"
    estimated_time: str = "30 min"


class CookbookDetail(BaseModel):
    id: str
    title: str
    description: str
    apis_used: list[str]
    difficulty: str
    estimated_time: str
    prerequisites: list[str]
    steps: list[CookbookStep]
    code_examples: dict[str, str]


class CookbookListResponse(BaseModel):
    cookbooks: list[CookbookSummary]
    total: int


# ─── Cookbook Data ────────────────────────────────────────────────────────────

COOKBOOKS: dict[str, dict[str, Any]] = {
    "razorpay-shiprocket-ecommerce": {
        "id": "razorpay-shiprocket-ecommerce",
        "title": "E-Commerce Payment + Shipping (Razorpay + Shiprocket)",
        "description": (
            "Build a complete e-commerce checkout flow: collect payment via Razorpay, "
            "verify the transaction, then auto-create a shipping order on Shiprocket "
            "with tracking. Covers webhooks, error handling, and order state management."
        ),
        "apis_used": ["/razorpay/razorpay-sdk", "/shiprocket/shiprocket-api"],
        "difficulty": "intermediate",
        "estimated_time": "45 min",
        "prerequisites": [
            "Razorpay account with API keys (Test mode works)",
            "Shiprocket account with API credentials",
            "Python 3.10+ with pip",
            "A basic understanding of webhooks",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Create a Razorpay order",
                "description": "Initialize the Razorpay client and create an order with amount, currency, and receipt.",
                "api": "/razorpay/razorpay-sdk",
                "language": "python",
                "code": '''import razorpay

rzp = razorpay.Client(auth=("rzp_test_XXXX", "secret_XXXX"))

order = rzp.order.create({
    "amount": 149900,       # ₹1,499 in paise
    "currency": "INR",
    "receipt": "order_001",
    "payment_capture": 1,   # Auto-capture
})
print(f"Razorpay Order: {order['id']}")
# Pass order['id'] to your frontend checkout form
''',
            },
            {
                "step_number": 2,
                "title": "Handle Razorpay payment webhook",
                "description": "Set up a webhook endpoint to receive payment confirmation. Verify the signature before trusting the event.",
                "api": "/razorpay/razorpay-sdk",
                "language": "python",
                "code": '''import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

RAZORPAY_WEBHOOK_SECRET = "your_webhook_secret"

@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    expected = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    event = payload["event"]

    if event == "payment.captured":
        payment = payload["payload"]["payment"]["entity"]
        order_id = payment["order_id"]
        amount = payment["amount"]
        print(f"Payment captured: {order_id} for ₹{amount / 100}")
        # Trigger Shiprocket order creation (step 3)
        await create_shiprocket_order(order_id, payment)

    return {"status": "ok"}
''',
            },
            {
                "step_number": 3,
                "title": "Create Shiprocket shipment after payment",
                "description": "Once payment is confirmed, automatically create a shipping order on Shiprocket with the customer's address and order details.",
                "api": "/shiprocket/shiprocket-api",
                "language": "python",
                "code": '''import requests

SHIPROCKET_TOKEN = "your_shiprocket_token"
SR_BASE = "https://apiv2.shiprocket.in/v1/external"

async def create_shiprocket_order(razorpay_order_id: str, payment: dict):
    headers = {
        "Authorization": f"Bearer {SHIPROCKET_TOKEN}",
        "Content-Type": "application/json",
    }

    order_payload = {
        "order_id": razorpay_order_id,
        "order_date": "2024-03-15 11:00",
        "pickup_location": "Primary",
        "billing_customer_name": payment["notes"].get("name", "Customer"),
        "billing_address": payment["notes"].get("address", ""),
        "billing_city": payment["notes"].get("city", ""),
        "billing_pincode": payment["notes"].get("pincode", ""),
        "billing_state": payment["notes"].get("state", ""),
        "billing_country": "India",
        "billing_email": payment.get("email", ""),
        "billing_phone": payment.get("contact", ""),
        "shipping_is_billing": True,
        "order_items": [
            {
                "name": "Product",
                "sku": "SKU001",
                "units": 1,
                "selling_price": payment["amount"] / 100,
            }
        ],
        "payment_method": "Prepaid",
        "sub_total": payment["amount"] / 100,
        "length": 20, "breadth": 15, "height": 10, "weight": 0.5,
    }

    resp = requests.post(
        f"{SR_BASE}/orders/create/adhoc",
        json=order_payload,
        headers=headers,
    )
    result = resp.json()
    print(f"Shiprocket order created: {result.get('order_id')}")

    # Auto-assign courier
    if "shipment_id" in result:
        awb = requests.post(f"{SR_BASE}/courier/assign/awb", json={
            "shipment_id": result["shipment_id"],
        }, headers=headers)
        print(f"AWB assigned: {awb.json().get('response', {}).get('data', {}).get('awb_code')}")
''',
            },
            {
                "step_number": 4,
                "title": "Track shipment and notify customer",
                "description": "Poll Shiprocket for tracking updates and send status to the customer.",
                "api": "/shiprocket/shiprocket-api",
                "language": "python",
                "code": '''def get_tracking(awb_code: str) -> dict:
    headers = {"Authorization": f"Bearer {SHIPROCKET_TOKEN}"}
    resp = requests.get(
        f"{SR_BASE}/courier/track/awb/{awb_code}",
        headers=headers,
    )
    tracking = resp.json()["tracking_data"]
    return {
        "status": tracking["shipment_status"],
        "current_location": tracking.get("current_status", ""),
        "estimated_delivery": tracking.get("etd", ""),
    }

# Example usage
status = get_tracking("AWB123456")
print(f"Shipment: {status['status']} — ETA: {status['estimated_delivery']}")
''',
            },
        ],
        "code_examples": {
            "full_python": '''"""Complete Razorpay + Shiprocket E-Commerce Flow"""
import razorpay
import requests
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

# Config
RZP_KEY = "rzp_test_XXXX"
RZP_SECRET = "secret_XXXX"
RZP_WEBHOOK_SECRET = "webhook_secret"
SR_TOKEN = "shiprocket_token"
SR_BASE = "https://apiv2.shiprocket.in/v1/external"

rzp = razorpay.Client(auth=(RZP_KEY, RZP_SECRET))

@app.post("/api/orders/create")
async def create_order(amount: int, customer_name: str, address: str, city: str, pincode: str):
    order = rzp.order.create({
        "amount": amount * 100,
        "currency": "INR",
        "receipt": f"order_{customer_name}",
        "notes": {"name": customer_name, "address": address, "city": city, "pincode": pincode},
    })
    return {"order_id": order["id"], "amount": order["amount"]}

@app.post("/webhooks/razorpay")
async def handle_payment(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(RZP_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(400, "Bad signature")
    payload = await request.json()
    if payload["event"] == "payment.captured":
        payment = payload["payload"]["payment"]["entity"]
        # Create shipping order
        headers = {"Authorization": f"Bearer {SR_TOKEN}", "Content-Type": "application/json"}
        requests.post(f"{SR_BASE}/orders/create/adhoc", json={
            "order_id": payment["order_id"],
            "order_date": "2024-03-15",
            "pickup_location": "Primary",
            "billing_customer_name": payment["notes"]["name"],
            "billing_address": payment["notes"]["address"],
            "billing_city": payment["notes"]["city"],
            "billing_pincode": payment["notes"]["pincode"],
            "billing_state": "Karnataka",
            "billing_country": "India",
            "billing_phone": payment["contact"],
            "shipping_is_billing": True,
            "order_items": [{"name": "Product", "sku": "SKU001", "units": 1, "selling_price": payment["amount"] / 100}],
            "payment_method": "Prepaid",
            "sub_total": payment["amount"] / 100,
            "length": 20, "breadth": 15, "height": 10, "weight": 0.5,
        }, headers=headers)
    return {"status": "ok"}
''',
        },
    },
    "razorpay-msg91-otp-payment": {
        "id": "razorpay-msg91-otp-payment",
        "title": "OTP Verification + Payment (MSG91 + Razorpay)",
        "description": (
            "Implement phone-number verification via MSG91 OTP before collecting payment "
            "through Razorpay. Common pattern for COD-to-prepaid conversion, high-value "
            "transactions, and fraud prevention."
        ),
        "apis_used": ["/msg91/msg91-api", "/razorpay/razorpay-sdk"],
        "difficulty": "beginner",
        "estimated_time": "30 min",
        "prerequisites": [
            "MSG91 account with OTP template approved",
            "Razorpay test mode keys",
            "Python 3.10+ with FastAPI",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Send OTP via MSG91",
                "description": "Trigger an OTP to the customer's mobile number before showing the payment form.",
                "api": "/msg91/msg91-api",
                "language": "python",
                "code": '''import requests

MSG91_AUTH_KEY = "your_auth_key"
MSG91_TEMPLATE_ID = "your_template_id"

def send_otp(mobile: str) -> bool:
    """Send OTP to Indian mobile number."""
    resp = requests.post("https://control.msg91.com/api/v5/otp", json={
        "template_id": MSG91_TEMPLATE_ID,
        "mobile": f"91{mobile}",
        "otp_length": 6,
        "otp_expiry": 5,
    }, headers={"authkey": MSG91_AUTH_KEY})
    return resp.json().get("type") == "success"
''',
            },
            {
                "step_number": 2,
                "title": "Verify OTP",
                "description": "Validate the OTP entered by the user. Only proceed to payment if OTP is valid.",
                "api": "/msg91/msg91-api",
                "language": "python",
                "code": '''def verify_otp(mobile: str, otp: str) -> bool:
    """Verify OTP — returns True if valid."""
    resp = requests.get("https://control.msg91.com/api/v5/otp/verify", params={
        "mobile": f"91{mobile}",
        "otp": otp,
    }, headers={"authkey": MSG91_AUTH_KEY})
    return resp.json().get("type") == "success"
''',
            },
            {
                "step_number": 3,
                "title": "Create Razorpay order after OTP verification",
                "description": "Only create a payment order after the phone number is verified, reducing fraud.",
                "api": "/razorpay/razorpay-sdk",
                "language": "python",
                "code": '''import razorpay
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
rzp = razorpay.Client(auth=("rzp_test_XXXX", "secret_XXXX"))

class CheckoutRequest(BaseModel):
    mobile: str
    otp: str
    amount: int  # in INR

@app.post("/api/checkout")
async def checkout(req: CheckoutRequest):
    # Step 1: Verify OTP
    if not verify_otp(req.mobile, req.otp):
        raise HTTPException(400, "Invalid OTP")

    # Step 2: Create Razorpay order (OTP verified)
    order = rzp.order.create({
        "amount": req.amount * 100,
        "currency": "INR",
        "receipt": f"verified_{req.mobile}",
        "notes": {"verified_mobile": req.mobile},
    })

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "verified": True,
    }
''',
            },
        ],
        "code_examples": {
            "full_python": '''"""MSG91 OTP + Razorpay Payment — Complete Flow"""
import razorpay
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

MSG91_AUTH_KEY = "your_auth_key"
MSG91_TEMPLATE_ID = "your_template_id"
rzp = razorpay.Client(auth=("rzp_test_XXXX", "secret_XXXX"))

class OTPRequest(BaseModel):
    mobile: str

class VerifyAndPayRequest(BaseModel):
    mobile: str
    otp: str
    amount: int

@app.post("/api/otp/send")
async def send(req: OTPRequest):
    resp = requests.post("https://control.msg91.com/api/v5/otp", json={
        "template_id": MSG91_TEMPLATE_ID, "mobile": f"91{req.mobile}",
        "otp_length": 6, "otp_expiry": 5,
    }, headers={"authkey": MSG91_AUTH_KEY})
    if resp.json().get("type") != "success":
        raise HTTPException(500, "Failed to send OTP")
    return {"message": "OTP sent"}

@app.post("/api/otp/verify-and-pay")
async def verify_and_pay(req: VerifyAndPayRequest):
    resp = requests.get("https://control.msg91.com/api/v5/otp/verify", params={
        "mobile": f"91{req.mobile}", "otp": req.otp,
    }, headers={"authkey": MSG91_AUTH_KEY})
    if resp.json().get("type") != "success":
        raise HTTPException(400, "Invalid OTP")
    order = rzp.order.create({
        "amount": req.amount * 100, "currency": "INR",
        "receipt": f"verified_{req.mobile}",
    })
    return {"order_id": order["id"], "amount": order["amount"]}
''',
        },
    },
    "ondc-buyer-app": {
        "id": "ondc-buyer-app",
        "title": "ONDC Buyer App (Beckn Protocol Flow)",
        "description": (
            "Build an ONDC-compliant buyer application implementing the full Beckn Protocol "
            "flow: search → on_search → select → on_select → init → on_init → confirm → on_confirm. "
            "Includes Ed25519 request signing, DNS registration, and async callback handling."
        ),
        "apis_used": ["/ondc/protocol-specs"],
        "difficulty": "advanced",
        "estimated_time": "2 hours",
        "prerequisites": [
            "ONDC staging account and subscriber ID",
            "Ed25519 signing key pair generated",
            "DNS TXT record for subscriber verification",
            "Understanding of async webhook-based APIs",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Generate Ed25519 key pair and register on ONDC",
                "description": "ONDC requires Ed25519 cryptographic signing for all requests. Generate a key pair and register your subscriber ID.",
                "api": "/ondc/protocol-specs",
                "language": "python",
                "code": '''import nacl.signing
import base64

# Generate Ed25519 key pair
signing_key = nacl.signing.SigningKey.generate()
verify_key = signing_key.verify_key

private_key_b64 = base64.b64encode(signing_key.encode()).decode()
public_key_b64 = base64.b64encode(verify_key.encode()).decode()

print(f"Private Key (keep secret): {private_key_b64}")
print(f"Public Key (register on ONDC): {public_key_b64}")

# Add a DNS TXT record at:
# _ondc.your-buyer-app.com TXT "signing_public_key={public_key_b64}"
''',
            },
            {
                "step_number": 2,
                "title": "Send /search request to ONDC gateway",
                "description": "Construct a Beckn /search request with proper context, intent, and fulfillment fields. Sign with Ed25519.",
                "api": "/ondc/protocol-specs",
                "language": "python",
                "code": '''import json
import nacl.signing
import base64
import requests
from datetime import datetime, timezone
import uuid

ONDC_GATEWAY = "https://staging.gateway.ondc.org/search"
BAP_ID = "your-buyer-app.com"
BAP_URI = "https://your-buyer-app.com/ondc"

def create_search_request(item_name: str, city_code: str, gps: str) -> dict:
    return {
        "context": {
            "domain": "nic2004:52110",
            "action": "search",
            "country": "IND",
            "city": city_code,
            "core_version": "1.2.0",
            "bap_id": BAP_ID,
            "bap_uri": BAP_URI,
            "transaction_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "message": {
            "intent": {
                "item": {"descriptor": {"name": item_name}},
                "fulfillment": {
                    "end": {"location": {"gps": gps}}
                },
            }
        },
    }

def sign_and_send(request_body: dict) -> requests.Response:
    signing_key = nacl.signing.SigningKey(base64.b64decode("YOUR_PRIVATE_KEY_B64"))
    body_bytes = json.dumps(request_body, separators=(",", ":")).encode()
    signed = signing_key.sign(body_bytes)
    sig_b64 = base64.b64encode(signed.signature).decode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": (
            f\'Signature keyId="{BAP_ID}|key1|ed25519",\'
            f\'algorithm="ed25519",\'
            f\'headers="(created) (expires) digest",\'
            f\'signature="{sig_b64}"\'
        ),
    }
    return requests.post(ONDC_GATEWAY, json=request_body, headers=headers, timeout=30)

# Search for "atta" in Bangalore
search_req = create_search_request("atta", "std:080", "12.9716,77.5946")
resp = sign_and_send(search_req)
print(f"Search sent: {resp.status_code}")
# ONDC will POST results to BAP_URI + /on_search asynchronously
''',
            },
            {
                "step_number": 3,
                "title": "Handle /on_search callback",
                "description": "ONDC sends search results asynchronously to your BAP URI. Parse catalog items from multiple sellers.",
                "api": "/ondc/protocol-specs",
                "language": "python",
                "code": '''from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/ondc/on_search")
async def on_search(request: Request):
    """Handle ONDC on_search callback with catalog results."""
    payload = await request.json()
    context = payload["context"]
    catalog = payload["message"]["catalog"]

    providers = catalog.get("bpp/providers", [])
    for provider in providers:
        provider_name = provider["descriptor"]["name"]
        items = provider.get("items", [])
        for item in items:
            item_name = item["descriptor"]["name"]
            price = item["price"]["value"]
            print(f"[{provider_name}] {item_name}: ₹{price}")

    # Store results, let user select items
    return {"context": context, "message": {"ack": {"status": "ACK"}}}
''',
            },
            {
                "step_number": 4,
                "title": "Select items and confirm order",
                "description": "Send /select, /init, and /confirm requests to complete the purchase flow with the chosen seller.",
                "api": "/ondc/protocol-specs",
                "language": "python",
                "code": '''def create_select_request(transaction_id: str, provider_id: str, item_ids: list[str]) -> dict:
    """Create a /select request for chosen items from a provider."""
    return {
        "context": {
            "domain": "nic2004:52110",
            "action": "select",
            "country": "IND",
            "core_version": "1.2.0",
            "bap_id": BAP_ID,
            "bap_uri": BAP_URI,
            "bpp_id": "seller-app.com",
            "bpp_uri": "https://seller-app.com/ondc",
            "transaction_id": transaction_id,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "message": {
            "order": {
                "provider": {"id": provider_id},
                "items": [{"id": iid, "quantity": {"count": 1}} for iid in item_ids],
            }
        },
    }

def create_confirm_request(transaction_id: str, order_details: dict) -> dict:
    """Create a /confirm request to finalize the order."""
    return {
        "context": {
            "domain": "nic2004:52110",
            "action": "confirm",
            "country": "IND",
            "core_version": "1.2.0",
            "bap_id": BAP_ID,
            "bap_uri": BAP_URI,
            "transaction_id": transaction_id,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "message": {"order": order_details},
    }

# Flow: search → on_search → select → on_select → init → on_init → confirm → on_confirm
''',
            },
        ],
        "code_examples": {
            "full_python": '''"""ONDC Buyer App — Full Beckn Protocol Implementation"""
# See individual steps above for the complete flow.
# Key points:
# 1. All requests must be Ed25519 signed
# 2. All responses come via async callbacks to your BAP URI
# 3. Flow: search → on_search → select → on_select → init → on_init → confirm → on_confirm
# 4. Each step requires handling the callback before proceeding
# 5. Transaction ID ties the entire flow together
''',
        },
    },
    "zerodha-algo-trading": {
        "id": "zerodha-algo-trading",
        "title": "Algorithmic Trading Bot (Zerodha Kite API)",
        "description": (
            "Build a simple moving-average crossover trading bot using Zerodha's Kite Connect API. "
            "Covers authentication, market data via WebSocket, order placement, and position management."
        ),
        "apis_used": ["/zerodha/kite-api"],
        "difficulty": "advanced",
        "estimated_time": "1 hour",
        "prerequisites": [
            "Zerodha Demat + Trading account",
            "Kite Connect API subscription (₹2000/month)",
            "Python 3.10+ with kiteconnect package",
            "Basic understanding of trading concepts (SMA, orders)",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Authenticate with Kite Connect",
                "description": "Generate a login URL, get the request token after user login, and exchange for access token.",
                "api": "/zerodha/kite-api",
                "language": "python",
                "code": '''from kiteconnect import KiteConnect

API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

kite = KiteConnect(api_key=API_KEY)

# Step 1: Redirect user to login
print(f"Login URL: {kite.login_url()}")

# Step 2: After login, user is redirected with request_token
def authenticate(request_token: str):
    data = kite.generate_session(request_token, api_secret=API_SECRET)
    kite.set_access_token(data["access_token"])
    print(f"Authenticated. Access token: {data['access_token'][:20]}...")
    return data["access_token"]
''',
            },
            {
                "step_number": 2,
                "title": "Stream live market data via WebSocket",
                "description": "Subscribe to live tick data for instruments using Kite's WebSocket feed.",
                "api": "/zerodha/kite-api",
                "language": "python",
                "code": '''from kiteconnect import KiteTicker
import pandas as pd
from collections import deque

# Store last N prices for SMA calculation
price_history = deque(maxlen=50)

def on_ticks(ws, ticks):
    for tick in ticks:
        ltp = tick["last_price"]
        price_history.append(ltp)

        if len(price_history) >= 50:
            sma_20 = sum(list(price_history)[-20:]) / 20
            sma_50 = sum(price_history) / 50

            if sma_20 > sma_50:
                print(f"BUY signal: SMA20={sma_20:.2f} > SMA50={sma_50:.2f}, LTP=₹{ltp}")
                place_order("BUY", tick["instrument_token"])
            elif sma_20 < sma_50:
                print(f"SELL signal: SMA20={sma_20:.2f} < SMA50={sma_50:.2f}, LTP=₹{ltp}")
                place_order("SELL", tick["instrument_token"])

def on_connect(ws, response):
    # Subscribe to NIFTY 50 (instrument_token: 256265)
    ws.subscribe([256265])
    ws.set_mode(ws.MODE_LTP, [256265])

kws = KiteTicker(API_KEY, kite.access_token)
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.connect(threaded=True)
''',
            },
            {
                "step_number": 3,
                "title": "Place orders based on signals",
                "description": "Execute BUY/SELL orders when the SMA crossover signal triggers.",
                "api": "/zerodha/kite-api",
                "language": "python",
                "code": '''POSITION_SIZE = 50  # Number of shares per trade
TRADINGSYMBOL = "NIFTY24MARFUT"

def place_order(signal: str, instrument_token: int):
    """Place a market order based on trading signal."""
    try:
        transaction_type = kite.TRANSACTION_TYPE_BUY if signal == "BUY" else kite.TRANSACTION_TYPE_SELL

        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NFO,
            tradingsymbol=TRADINGSYMBOL,
            transaction_type=transaction_type,
            quantity=POSITION_SIZE,
            order_type=kite.ORDER_TYPE_MARKET,
            product=kite.PRODUCT_MIS,  # Intraday
        )
        print(f"Order placed: {signal} {POSITION_SIZE} {TRADINGSYMBOL} — ID: {order_id}")

    except Exception as e:
        print(f"Order failed: {e}")

def check_positions():
    """Check current open positions."""
    positions = kite.positions()
    for pos in positions["net"]:
        if pos["quantity"] != 0:
            pnl = pos["pnl"]
            print(f"{pos['tradingsymbol']}: {pos['quantity']} qty, P&L: ₹{pnl:.2f}")
''',
            },
            {
                "step_number": 4,
                "title": "Risk management — stop-loss and square-off",
                "description": "Implement stop-loss orders and auto square-off before market close.",
                "api": "/zerodha/kite-api",
                "language": "python",
                "code": '''import schedule
import time

MAX_LOSS = 5000  # Maximum loss in INR before stopping

def check_risk():
    """Monitor P&L and exit if max loss exceeded."""
    positions = kite.positions()
    total_pnl = sum(p["pnl"] for p in positions["net"] if p["quantity"] != 0)

    if total_pnl < -MAX_LOSS:
        print(f"MAX LOSS hit: ₹{total_pnl}. Squaring off all positions.")
        square_off_all()

def square_off_all():
    """Close all open positions."""
    positions = kite.positions()
    for pos in positions["net"]:
        if pos["quantity"] != 0:
            txn = kite.TRANSACTION_TYPE_SELL if pos["quantity"] > 0 else kite.TRANSACTION_TYPE_BUY
            kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=pos["exchange"],
                tradingsymbol=pos["tradingsymbol"],
                transaction_type=txn,
                quantity=abs(pos["quantity"]),
                order_type=kite.ORDER_TYPE_MARKET,
                product=kite.PRODUCT_MIS,
            )
            print(f"Squared off: {pos['tradingsymbol']}")

# Auto square-off at 3:15 PM IST
schedule.every().day.at("15:15").do(square_off_all)

# Risk check every minute
schedule.every(1).minutes.do(check_risk)
''',
            },
        ],
        "code_examples": {
            "full_python": '''"""Zerodha Kite — SMA Crossover Algo Trading Bot"""
# Complete bot combines all 4 steps:
# 1. Authenticate via Kite Connect
# 2. Subscribe to live ticks via WebSocket
# 3. Calculate SMA(20) and SMA(50) crossover
# 4. Place orders on signal, manage risk with stop-loss
# 5. Auto square-off at 3:15 PM IST
# Run: python bot.py (after authenticating)
''',
        },
    },
    "gstn-einvoice": {
        "id": "gstn-einvoice",
        "title": "GST E-Invoicing Flow (GSTN via GSP)",
        "description": (
            "Generate GST-compliant e-invoices using the GSTN API through a GSP (GST Suvidha Provider). "
            "Covers authentication, IRN generation, QR code signing, and e-way bill linking."
        ),
        "apis_used": ["/gstn/gst-api"],
        "difficulty": "intermediate",
        "estimated_time": "45 min",
        "prerequisites": [
            "GSTIN (GST Identification Number) for your business",
            "GSP account (ClearTax, MasterGST, or similar)",
            "GSP API credentials (client_id, client_secret)",
            "Understanding of GST invoice structure",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Authenticate with GSP",
                "description": "All GSTN API calls go through a licensed GSP. Authenticate with your GSP to get an auth token.",
                "api": "/gstn/gst-api",
                "language": "python",
                "code": '''import requests

GSP_BASE = "https://api.mastergst.com"
GSP_CLIENT_ID = "your_client_id"
GSP_CLIENT_SECRET = "your_client_secret"
GSTIN = "29AABCT1332L1ZL"

def authenticate_gsp() -> str:
    """Get auth token from GSP."""
    resp = requests.post(f"{GSP_BASE}/einvoice/authenticate", params={
        "email": "accounts@yourcompany.com",
        "gstin": GSTIN,
        "client_id": GSP_CLIENT_ID,
        "client_secret": GSP_CLIENT_SECRET,
    })
    data = resp.json()
    if data["status_cd"] != "1":
        raise Exception(f"Auth failed: {data.get('error', {}).get('message')}")
    return data["data"]["AuthToken"]

token = authenticate_gsp()
print(f"Authenticated. Token: {token[:20]}...")
''',
            },
            {
                "step_number": 2,
                "title": "Generate e-invoice (IRN)",
                "description": "Submit invoice details to generate an IRN (Invoice Reference Number) with signed QR code.",
                "api": "/gstn/gst-api",
                "language": "python",
                "code": '''from datetime import datetime

def generate_einvoice(token: str) -> dict:
    """Generate e-invoice and get IRN + signed QR code."""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    invoice = {
        "Version": "1.1",
        "TranDtls": {"TaxSch": "GST", "SupTyp": "B2B"},
        "DocDtls": {
            "Typ": "INV",
            "No": f"INV-{datetime.now().strftime('%Y%m%d')}-001",
            "Dt": datetime.now().strftime("%d/%m/%Y"),
        },
        "SellerDtls": {
            "Gstin": "29AABCT1332L1ZL",
            "LglNm": "Your Company Pvt Ltd",
            "Addr1": "100 MG Road", "Loc": "Bangalore",
            "Pin": 560001, "Stcd": "29",
        },
        "BuyerDtls": {
            "Gstin": "27AADCB2230M1ZP",
            "LglNm": "Buyer Company Ltd",
            "Addr1": "Andheri East", "Loc": "Mumbai",
            "Pin": 400053, "Stcd": "27",
        },
        "ItemList": [{
            "SlNo": "1",
            "PrdDesc": "Annual Software License",
            "HsnCd": "998314",
            "Qty": 1, "Unit": "NOS",
            "UnitPrice": 100000, "TotAmt": 100000,
            "AssAmt": 100000, "GstRt": 18,
            "IgstAmt": 18000, "TotItemVal": 118000,
        }],
        "ValDtls": {
            "AssVal": 100000, "IgstVal": 18000, "TotInvVal": 118000,
        },
    }

    resp = requests.post(
        f"{GSP_BASE}/einvoice/type/GENERATE_IRN/version/V1_03",
        json=invoice, headers=headers,
    )
    result = resp.json()

    if result["status_cd"] == "1":
        irn_data = result["data"]
        print(f"IRN: {irn_data['Irn']}")
        print(f"Ack No: {irn_data['AckNo']}")
        print(f"Ack Date: {irn_data['AckDt']}")
        return irn_data
    else:
        raise Exception(f"E-invoice failed: {result['error']}")

irn_data = generate_einvoice(token)
''',
            },
            {
                "step_number": 3,
                "title": "Cancel e-invoice if needed",
                "description": "Cancel an e-invoice within 24 hours of generation using the IRN.",
                "api": "/gstn/gst-api",
                "language": "python",
                "code": '''def cancel_einvoice(token: str, irn: str, reason: str = "Data entry mistake") -> dict:
    """Cancel an e-invoice within 24 hours."""
    # Reason codes: 1=Duplicate, 2=Data entry mistake, 3=Order cancelled, 4=Others
    reason_code = "2"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = requests.post(
        f"{GSP_BASE}/einvoice/type/CANCEL/version/V1_03",
        json={"Irn": irn, "CnlRsn": reason_code, "CnlRem": reason},
        headers=headers,
    )
    result = resp.json()
    if result["status_cd"] == "1":
        print(f"E-invoice {irn} cancelled successfully")
    return result
''',
            },
        ],
        "code_examples": {
            "full_python": '''"""GSTN E-Invoice — Complete Flow via GSP"""
# 1. Authenticate with GSP (ClearTax / MasterGST)
# 2. Construct invoice JSON per GSTN e-invoice schema v1.1
# 3. POST to GENERATE_IRN endpoint
# 4. Receive IRN, AckNo, AckDt, and SignedQRCode
# 5. Print QR code on invoice PDF
# 6. Optionally link to e-way bill for goods transport
# 7. Cancel within 24h if needed
#
# Important: All businesses with turnover > ₹5 Cr must use e-invoicing.
# E-invoice data auto-populates GSTR-1 return.
''',
        },
    },
}


def _to_summary(data: dict[str, Any]) -> CookbookSummary:
    return CookbookSummary(
        id=data["id"],
        title=data["title"],
        description=data["description"],
        apis_used=data["apis_used"],
        difficulty=data.get("difficulty", "intermediate"),
        estimated_time=data.get("estimated_time", "30 min"),
    )


def _to_detail(data: dict[str, Any]) -> CookbookDetail:
    steps = [
        CookbookStep(**step)
        for step in data["steps"]
    ]
    return CookbookDetail(
        id=data["id"],
        title=data["title"],
        description=data["description"],
        apis_used=data["apis_used"],
        difficulty=data.get("difficulty", "intermediate"),
        estimated_time=data.get("estimated_time", "30 min"),
        prerequisites=data.get("prerequisites", []),
        steps=steps,
        code_examples=data.get("code_examples", {}),
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=CookbookListResponse)
async def list_cookbooks() -> CookbookListResponse:
    """
    List all available integration cookbooks.

    Each cookbook is a step-by-step guide for integrating multiple Indian APIs
    together in common business flows.
    """
    if not flags.COOKBOOKS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    summaries = [_to_summary(cb) for cb in COOKBOOKS.values()]
    return CookbookListResponse(cookbooks=summaries, total=len(summaries))


@router.get("/{cookbook_id}", response_model=CookbookDetail)
async def get_cookbook(cookbook_id: str) -> CookbookDetail:
    """
    Get a specific integration cookbook with full steps and code examples.
    """
    if not flags.COOKBOOKS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    data = COOKBOOKS.get(cookbook_id)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Cookbook {cookbook_id!r} not found. Use GET /v1/cookbooks to list available cookbooks.",
        )

    return _to_detail(data)
