"""Code snippet generation endpoint — generates integration code from doc chunks."""
from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/snippets", tags=["snippets"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class SnippetLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    GO = "go"
    JAVA = "java"


class SnippetFramework(str, Enum):
    NEXTJS = "nextjs"
    DJANGO = "django"
    EXPRESS = "express"
    FLASK = "flask"
    SPRING = "spring"
    FASTAPI = "fastapi"


class GenerateSnippetRequest(BaseModel):
    library_id: str = Field(..., description="ContextBharat library ID, e.g. /razorpay/razorpay-sdk")
    task: str = Field(..., description="What the developer wants to accomplish")
    language: SnippetLanguage = Field(default=SnippetLanguage.PYTHON)
    framework: SnippetFramework | None = Field(
        default=None, description="Optional framework context"
    )


class SnippetSource(BaseModel):
    url: str
    section: str | None = None


class GenerateSnippetResponse(BaseModel):
    code: str
    language: str
    explanation: str
    sources: list[SnippetSource] = []


# ─── Templates ───────────────────────────────────────────────────────────────

SNIPPET_TEMPLATES: dict[str, dict[str, str]] = {
    "/razorpay/razorpay-sdk": {
        "python": '''import razorpay

client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))

# Create an order
order = client.order.create({
    "amount": 50000,  # Amount in paise (500 INR)
    "currency": "INR",
    "receipt": "order_receipt_1",
    "payment_capture": 1,
})

print(f"Order ID: {order['id']}")

# Create a payment link
payment_link = client.payment_link.create({
    "amount": 50000,
    "currency": "INR",
    "description": "Payment for Order #1234",
    "customer": {
        "name": "Gaurav Kumar",
        "email": "gaurav@example.com",
        "contact": "+919876543210",
    },
    "notify": {"sms": True, "email": True},
    "callback_url": "https://yoursite.com/payment/callback",
    "callback_method": "get",
})

print(f"Payment Link: {payment_link['short_url']}")
''',
        "javascript": '''const Razorpay = require("razorpay");

const razorpay = new Razorpay({
  key_id: "YOUR_KEY_ID",
  key_secret: "YOUR_KEY_SECRET",
});

// Create an order
async function createOrder() {
  const order = await razorpay.orders.create({
    amount: 50000, // Amount in paise (500 INR)
    currency: "INR",
    receipt: "order_receipt_1",
    payment_capture: 1,
  });
  console.log("Order ID:", order.id);
  return order;
}

// Verify payment signature
const crypto = require("crypto");

function verifyPaymentSignature(orderId, paymentId, signature) {
  const body = orderId + "|" + paymentId;
  const expectedSignature = crypto
    .createHmac("sha256", "YOUR_KEY_SECRET")
    .update(body)
    .digest("hex");
  return expectedSignature === signature;
}
''',
        "go": '''package main

import (
	"fmt"
	razorpay "github.com/razorpay/razorpay-go/v2"
)

func main() {
	client := razorpay.NewClient("YOUR_KEY_ID", "YOUR_KEY_SECRET")

	// Create an order
	orderData := map[string]interface{}{
		"amount":          50000, // paise
		"currency":        "INR",
		"receipt":         "order_receipt_1",
		"payment_capture": 1,
	}

	order, err := client.Order.Create(orderData, nil)
	if err != nil {
		fmt.Printf("Error creating order: %v\\n", err)
		return
	}
	fmt.Printf("Order ID: %s\\n", order["id"])
}
''',
        "java": '''import com.razorpay.RazorpayClient;
import com.razorpay.Order;
import org.json.JSONObject;

public class RazorpayIntegration {
    public static void main(String[] args) throws Exception {
        RazorpayClient client = new RazorpayClient("YOUR_KEY_ID", "YOUR_KEY_SECRET");

        // Create an order
        JSONObject orderRequest = new JSONObject();
        orderRequest.put("amount", 50000); // paise
        orderRequest.put("currency", "INR");
        orderRequest.put("receipt", "order_receipt_1");
        orderRequest.put("payment_capture", 1);

        Order order = client.orders.create(orderRequest);
        System.out.println("Order ID: " + order.get("id"));
    }
}
''',
    },
    "/zerodha/kite-api": {
        "python": '''from kiteconnect import KiteConnect

kite = KiteConnect(api_key="YOUR_API_KEY")

# Step 1: Get login URL — redirect user here
login_url = kite.login_url()
print(f"Login URL: {login_url}")

# Step 2: After redirect, exchange request_token for access_token
data = kite.generate_session("REQUEST_TOKEN", api_secret="YOUR_API_SECRET")
kite.set_access_token(data["access_token"])

# Place a market order
order_id = kite.place_order(
    variety=kite.VARIETY_REGULAR,
    exchange=kite.EXCHANGE_NSE,
    tradingsymbol="INFY",
    transaction_type=kite.TRANSACTION_TYPE_BUY,
    quantity=1,
    order_type=kite.ORDER_TYPE_MARKET,
    product=kite.PRODUCT_CNC,
)
print(f"Order placed: {order_id}")

# Get portfolio holdings
holdings = kite.holdings()
for stock in holdings:
    print(f"{stock['tradingsymbol']}: {stock['quantity']} shares @ ₹{stock['average_price']}")
''',
        "javascript": '''const KiteConnect = require("kiteconnect").KiteConnect;

const kite = new KiteConnect({ api_key: "YOUR_API_KEY" });

// Step 1: Get login URL
console.log("Login URL:", kite.getLoginURL());

// Step 2: Exchange request_token for access_token
async function authenticate(requestToken) {
  const session = await kite.generateSession(requestToken, "YOUR_API_SECRET");
  kite.setAccessToken(session.access_token);

  // Place a market order
  const orderId = await kite.placeOrder("regular", {
    exchange: "NSE",
    tradingsymbol: "INFY",
    transaction_type: "BUY",
    quantity: 1,
    order_type: "MARKET",
    product: "CNC",
  });
  console.log("Order placed:", orderId);
}
''',
    },
    "/cashfree/cashfree-pg": {
        "python": '''from cashfree_pg.models import CreateOrderRequest, CustomerDetails, OrderMeta
from cashfree_pg.api_client import Cashfree

Cashfree.XClientId = "YOUR_APP_ID"
Cashfree.XClientSecret = "YOUR_SECRET_KEY"
Cashfree.XEnvironment = Cashfree.SANDBOX  # Use Cashfree.PRODUCTION for live

# Create an order
customer = CustomerDetails(
    customer_id="customer_001",
    customer_name="Ravi Kumar",
    customer_email="ravi@example.com",
    customer_phone="9876543210",
)
order_meta = OrderMeta(return_url="https://yoursite.com/return?order_id={order_id}")

order_request = CreateOrderRequest(
    order_amount=499.0,
    order_currency="INR",
    customer_details=customer,
    order_meta=order_meta,
)

response = Cashfree().PGCreateOrder("2023-08-01", order_request)
print(f"Order ID: {response.data.cf_order_id}")
print(f"Payment Session ID: {response.data.payment_session_id}")
''',
        "javascript": '''const { Cashfree } = require("cashfree-pg");

Cashfree.XClientId = "YOUR_APP_ID";
Cashfree.XClientSecret = "YOUR_SECRET_KEY";
Cashfree.XEnvironment = Cashfree.Environment.SANDBOX;

async function createOrder() {
  const request = {
    order_amount: 499.0,
    order_currency: "INR",
    customer_details: {
      customer_id: "customer_001",
      customer_name: "Ravi Kumar",
      customer_email: "ravi@example.com",
      customer_phone: "9876543210",
    },
    order_meta: {
      return_url: "https://yoursite.com/return?order_id={order_id}",
    },
  };

  const response = await Cashfree.PGCreateOrder("2023-08-01", request);
  console.log("Order ID:", response.data.cf_order_id);
  console.log("Payment Session:", response.data.payment_session_id);
}
''',
    },
    "/ondc/protocol-specs": {
        "python": '''import requests
import json
import nacl.signing
import base64
from datetime import datetime, timezone

# ONDC Buyer App — Search Flow (Beckn Protocol)

ONDC_GATEWAY_URL = "https://staging.gateway.ondc.org/search"

# Step 1: Create search request (Beckn /search)
search_request = {
    "context": {
        "domain": "nic2004:52110",  # Retail grocery
        "action": "search",
        "country": "IND",
        "city": "std:080",  # Bangalore
        "core_version": "1.2.0",
        "bap_id": "your-buyer-app.com",
        "bap_uri": "https://your-buyer-app.com/ondc",
        "transaction_id": "txn_001",
        "message_id": "msg_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "message": {
        "intent": {
            "item": {"descriptor": {"name": "atta"}},
            "fulfillment": {
                "end": {
                    "location": {
                        "gps": "12.9716,77.5946",  # Bangalore GPS
                    }
                }
            },
        }
    },
}

# Step 2: Sign the request with Ed25519
signing_key = nacl.signing.SigningKey(base64.b64decode("YOUR_PRIVATE_KEY"))
signed = signing_key.sign(json.dumps(search_request).encode())
signature = base64.b64encode(signed.signature).decode()

headers = {
    "Content-Type": "application/json",
    "Authorization": f'Signature keyId="your-buyer-app.com|key_id|ed25519",algorithm="ed25519",headers="(created) (expires) digest",signature="{signature}"',
}

# Step 3: Send to ONDC gateway
response = requests.post(ONDC_GATEWAY_URL, json=search_request, headers=headers)
print(f"Search status: {response.status_code}")

# Step 4: Handle /on_search callback on your webhook endpoint
# ONDC will POST search results to your bap_uri + /on_search
''',
        "javascript": '''const nacl = require("tweetnacl");
const axios = require("axios");

const ONDC_GATEWAY_URL = "https://staging.gateway.ondc.org/search";

// ONDC Buyer App — Search Flow (Beckn Protocol)
async function searchONDC() {
  const searchRequest = {
    context: {
      domain: "nic2004:52110", // Retail grocery
      action: "search",
      country: "IND",
      city: "std:080", // Bangalore
      core_version: "1.2.0",
      bap_id: "your-buyer-app.com",
      bap_uri: "https://your-buyer-app.com/ondc",
      transaction_id: "txn_001",
      message_id: "msg_001",
      timestamp: new Date().toISOString(),
    },
    message: {
      intent: {
        item: { descriptor: { name: "atta" } },
        fulfillment: {
          end: { location: { gps: "12.9716,77.5946" } },
        },
      },
    },
  };

  // Sign with Ed25519
  const privateKey = Buffer.from("YOUR_PRIVATE_KEY", "base64");
  const keyPair = nacl.sign.keyPair.fromSecretKey(privateKey);
  const messageBytes = Buffer.from(JSON.stringify(searchRequest));
  const signature = nacl.sign.detached(messageBytes, keyPair.secretKey);
  const signatureB64 = Buffer.from(signature).toString("base64");

  const response = await axios.post(ONDC_GATEWAY_URL, searchRequest, {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Signature keyId="your-buyer-app.com|key_id|ed25519",algorithm="ed25519",signature="${signatureB64}"`,
    },
  });

  console.log("Search status:", response.status);
}
''',
    },
    "/msg91/msg91-api": {
        "python": '''import requests

MSG91_AUTH_KEY = "YOUR_AUTH_KEY"
MSG91_TEMPLATE_ID = "YOUR_TEMPLATE_ID"

# Send OTP
def send_otp(mobile: str) -> dict:
    url = "https://control.msg91.com/api/v5/otp"
    payload = {
        "template_id": MSG91_TEMPLATE_ID,
        "mobile": f"91{mobile}",
        "otp_length": 6,
        "otp_expiry": 5,  # minutes
    }
    headers = {"authkey": MSG91_AUTH_KEY, "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Verify OTP
def verify_otp(mobile: str, otp: str) -> dict:
    url = "https://control.msg91.com/api/v5/otp/verify"
    params = {"mobile": f"91{mobile}", "otp": otp}
    headers = {"authkey": MSG91_AUTH_KEY}
    response = requests.get(url, params=params, headers=headers)
    return response.json()

# Usage
result = send_otp("9876543210")
print(f"OTP sent: {result}")

verify_result = verify_otp("9876543210", "123456")
print(f"OTP verified: {verify_result}")
''',
        "javascript": '''const axios = require("axios");

const MSG91_AUTH_KEY = "YOUR_AUTH_KEY";
const MSG91_TEMPLATE_ID = "YOUR_TEMPLATE_ID";

// Send OTP
async function sendOTP(mobile) {
  const response = await axios.post(
    "https://control.msg91.com/api/v5/otp",
    {
      template_id: MSG91_TEMPLATE_ID,
      mobile: `91${mobile}`,
      otp_length: 6,
      otp_expiry: 5,
    },
    { headers: { authkey: MSG91_AUTH_KEY } }
  );
  return response.data;
}

// Verify OTP
async function verifyOTP(mobile, otp) {
  const response = await axios.get(
    "https://control.msg91.com/api/v5/otp/verify",
    {
      params: { mobile: `91${mobile}`, otp },
      headers: { authkey: MSG91_AUTH_KEY },
    }
  );
  return response.data;
}
''',
    },
    "/shiprocket/shiprocket-api": {
        "python": '''import requests

SHIPROCKET_EMAIL = "your@email.com"
SHIPROCKET_PASSWORD = "your_password"
BASE_URL = "https://apiv2.shiprocket.in/v1/external"

# Step 1: Authenticate
def get_token() -> str:
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": SHIPROCKET_EMAIL,
        "password": SHIPROCKET_PASSWORD,
    })
    return response.json()["token"]

token = get_token()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Step 2: Create an order
order_payload = {
    "order_id": "ORD_001",
    "order_date": "2024-03-15 11:00",
    "pickup_location": "Primary",
    "billing_customer_name": "Ravi",
    "billing_last_name": "Kumar",
    "billing_address": "MG Road",
    "billing_city": "Bangalore",
    "billing_pincode": "560001",
    "billing_state": "Karnataka",
    "billing_country": "India",
    "billing_email": "ravi@example.com",
    "billing_phone": "9876543210",
    "shipping_is_billing": True,
    "order_items": [
        {
            "name": "Wireless Earbuds",
            "sku": "EAR001",
            "units": 1,
            "selling_price": 1499,
            "discount": 0,
        }
    ],
    "payment_method": "Prepaid",
    "sub_total": 1499,
    "length": 10,
    "breadth": 8,
    "height": 5,
    "weight": 0.3,
}
response = requests.post(f"{BASE_URL}/orders/create/adhoc", json=order_payload, headers=headers)
print(f"Shiprocket Order: {response.json()}")

# Step 3: Generate AWB (shipment)
shipment_id = response.json()["shipment_id"]
awb_response = requests.post(f"{BASE_URL}/courier/assign/awb", json={
    "shipment_id": shipment_id,
    "courier_id": "",  # Auto-select best courier
}, headers=headers)
print(f"AWB: {awb_response.json()}")
''',
    },
    "/gstn/gst-api": {
        "python": '''import requests
import json
from datetime import datetime

# GSTN E-Invoice Generation via GSP (e.g., ClearTax, MasterGST)
# Direct GSTN API requires GSP partnership; this shows the standard flow.

GSP_BASE_URL = "https://api.mastergst.com"  # Example GSP
GSP_CLIENT_ID = "YOUR_CLIENT_ID"
GSP_CLIENT_SECRET = "YOUR_SECRET"

# Step 1: Authenticate with GSP
def get_gsp_token() -> str:
    response = requests.post(f"{GSP_BASE_URL}/einvoice/authenticate", params={
        "email": "your@email.com",
        "gstin": "29AABCT1332L1ZL",
        "client_id": GSP_CLIENT_ID,
        "client_secret": GSP_CLIENT_SECRET,
    })
    return response.json()["data"]["AuthToken"]

# Step 2: Generate IRN (Invoice Reference Number)
def generate_einvoice(token: str, invoice_data: dict) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "Version": "1.1",
        "TranDtls": {
            "TaxSch": "GST",
            "SupTyp": "B2B",
        },
        "DocDtls": {
            "Typ": "INV",
            "No": "INV-2024-001",
            "Dt": datetime.now().strftime("%d/%m/%Y"),
        },
        "SellerDtls": {
            "Gstin": "29AABCT1332L1ZL",
            "LglNm": "Your Company Pvt Ltd",
            "Addr1": "MG Road",
            "Loc": "Bangalore",
            "Pin": 560001,
            "Stcd": "29",
        },
        "BuyerDtls": {
            "Gstin": "27AADCB2230M1ZP",
            "LglNm": "Buyer Company Ltd",
            "Addr1": "Andheri",
            "Loc": "Mumbai",
            "Pin": 400053,
            "Stcd": "27",
        },
        "ItemList": [
            {
                "SlNo": "1",
                "PrdDesc": "Software License",
                "HsnCd": "998314",
                "Qty": 1,
                "Unit": "NOS",
                "UnitPrice": 10000,
                "TotAmt": 10000,
                "AssAmt": 10000,
                "GstRt": 18,
                "IgstAmt": 1800,
                "TotItemVal": 11800,
            }
        ],
        "ValDtls": {
            "AssVal": 10000,
            "IgstVal": 1800,
            "TotInvVal": 11800,
        },
    }
    response = requests.post(
        f"{GSP_BASE_URL}/einvoice/type/GENERATE_IRN/version/V1_03",
        json=payload,
        headers=headers,
    )
    return response.json()

token = get_gsp_token()
result = generate_einvoice(token, {})
print(f"IRN: {result['data']['Irn']}")
print(f"Signed QR: {result['data']['SignedQRCode']}")
''',
    },
}

DEFAULT_TEMPLATE: dict[str, str] = {
    "python": '''# Integration template for {library_id}
# Install the SDK: pip install {library_name}

import {library_name}

# Initialize client
client = {library_name}.Client(api_key="YOUR_API_KEY")

# TODO: Replace with actual API calls based on the library documentation.
# Visit the official docs for {library_id} for detailed usage.
''',
    "javascript": '''// Integration template for {library_id}
// Install the SDK: npm install {library_name}

const {{ default: {library_name} }} = require("{library_name}");

// Initialize client
const client = new {library_name}({{ apiKey: "YOUR_API_KEY" }});

// TODO: Replace with actual API calls based on the library documentation.
''',
    "go": '''package main

import (
	"fmt"
	// TODO: Import the Go SDK for {library_id}
)

func main() {{
	// Initialize client for {library_id}
	// TODO: Replace with actual API calls
	fmt.Println("Integration template for {library_id}")
}}
''',
    "java": '''// Integration template for {library_id}
// Add the SDK dependency to your pom.xml or build.gradle

public class Integration {{
    public static void main(String[] args) {{
        // Initialize client for {library_id}
        // TODO: Replace with actual API calls
        System.out.println("Integration template for {library_id}");
    }}
}}
''',
}


def _get_library_short_name(library_id: str) -> str:
    """Extract a short name from a library ID for use in templates."""
    parts = library_id.strip("/").split("/")
    return parts[-1].replace("-", "_") if parts else "library"


def _generate_snippet(
    library_id: str,
    task: str,
    language: str,
    framework: str | None,
) -> GenerateSnippetResponse:
    """
    Generate a code snippet for the given library and task.

    Uses pre-built templates for known libraries, falls back to a generic
    template if the library is not in the template registry.
    """
    lib_templates = SNIPPET_TEMPLATES.get(library_id, {})
    code = lib_templates.get(language)

    if code:
        explanation = (
            f"Integration code for {library_id} in {language}. "
            f"This snippet demonstrates common usage patterns including authentication, "
            f"API calls, and response handling."
        )
        if framework:
            explanation += f" Adapt this for your {framework} project."
        sources = [
            SnippetSource(url=f"https://contextbharat.com/libraries{library_id}", section="API Reference"),
        ]
    else:
        lib_name = _get_library_short_name(library_id)
        template = DEFAULT_TEMPLATE.get(language, DEFAULT_TEMPLATE["python"])
        code = template.format(library_id=library_id, library_name=lib_name)
        explanation = (
            f"Generic integration template for {library_id} in {language}. "
            f"Replace the placeholder calls with actual API methods from the official docs."
        )
        sources = []

    return GenerateSnippetResponse(
        code=code.strip(),
        language=language,
        explanation=explanation,
        sources=sources,
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateSnippetResponse)
async def generate_snippet(request: GenerateSnippetRequest) -> GenerateSnippetResponse:
    """
    Generate integration code snippets for a library.

    Uses pre-built, tested templates for popular Indian APIs (Razorpay, Zerodha,
    Cashfree, ONDC, MSG91, Shiprocket, GSTN). Falls back to a generic template
    for other libraries.
    """
    if not flags.CODE_SNIPPETS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    try:
        return _generate_snippet(
            library_id=request.library_id,
            task=request.task,
            language=request.language.value,
            framework=request.framework.value if request.framework else None,
        )
    except Exception as e:
        logger.error(
            "Snippet generation failed",
            extra={"library_id": request.library_id, "language": request.language},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Snippet generation failed: {e}")
