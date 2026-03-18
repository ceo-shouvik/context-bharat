"""Error pattern database — common errors and fixes for Indian APIs."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/errors", tags=["errors"])


# ── Pydantic Models ──────────────────────────────────────────────


class ErrorPattern(BaseModel):
    """A known error pattern with solution."""

    id: str = Field(..., description="Unique ID for this error pattern")
    library_id: str
    error_code: str
    error_message: str
    solution: str
    language: str = Field(
        default="python", description="Programming language for code examples in solution"
    )
    upvotes: int = Field(default=0, description="Community upvote count")
    contributed_by: str = Field(
        default="system", description="Who contributed this pattern"
    )


class ErrorPatternListResponse(BaseModel):
    """Response containing error patterns for a library."""

    library_id: str
    patterns: list[ErrorPattern]
    total: int


class SubmitErrorPatternRequest(BaseModel):
    """Request to submit a new community-contributed error pattern."""

    library_id: str = Field(
        ..., description="Canonical library ID, e.g. /razorpay/razorpay-sdk"
    )
    error_code: str = Field(
        ..., description="Error code or HTTP status code", max_length=100
    )
    error_message: str = Field(
        ..., description="The actual error message the developer encountered", max_length=1000
    )
    solution: str = Field(
        ...,
        description="Step-by-step fix with code if applicable",
        min_length=10,
        max_length=5000,
    )
    language: str = Field(
        default="python",
        description="Programming language context",
        pattern=r"^(python|javascript|typescript|java|go|ruby|php|csharp|curl)$",
    )


class SubmitErrorPatternResponse(BaseModel):
    """Response after submitting a new error pattern."""

    id: str
    library_id: str
    error_code: str
    submitted: bool


# ── Pre-populated Error Pattern Database ─────────────────────────

_ERROR_PATTERNS: dict[str, list[dict]] = {
    "razorpay": [
        {
            "id": "rzp-001",
            "library_id": "/razorpay/razorpay-sdk",
            "error_code": "BAD_REQUEST_ERROR",
            "error_message": "The amount must be at least INR 1.00 (amount: 100 is in paise, so this is INR 1.00)",
            "solution": (
                "Razorpay expects amounts in paise (smallest currency unit). "
                "INR 500 must be sent as 50000. Common mistake: sending the "
                "rupee amount directly.\n\n"
                "```python\n"
                "# Wrong\n"
                "order = razorpay_client.order.create({\n"
                "    'amount': 500,  # This is INR 5.00, not INR 500\n"
                "    'currency': 'INR'\n"
                "})\n\n"
                "# Correct\n"
                "amount_inr = 500\n"
                "order = razorpay_client.order.create({\n"
                "    'amount': amount_inr * 100,  # 50000 paise = INR 500\n"
                "    'currency': 'INR'\n"
                "})\n"
                "```"
            ),
            "language": "python",
            "upvotes": 47,
            "contributed_by": "system",
        },
        {
            "id": "rzp-002",
            "library_id": "/razorpay/razorpay-sdk",
            "error_code": "AUTHENTICATION_ERROR",
            "error_message": "Authentication failed: key_id or key_secret is invalid",
            "solution": (
                "Check that you are using the correct key pair for the "
                "environment. Test mode keys start with `rzp_test_`, live mode "
                "keys start with `rzp_live_`.\n\n"
                "```python\n"
                "import razorpay\n\n"
                "# Make sure environment matches\n"
                "client = razorpay.Client(\n"
                "    auth=(os.environ['RAZORPAY_KEY_ID'],\n"
                "          os.environ['RAZORPAY_KEY_SECRET'])\n"
                ")\n\n"
                "# Verify: test keys should only be used with test dashboard\n"
                "# Live keys only work after KYC activation on Razorpay dashboard\n"
                "```\n\n"
                "Also verify: your API keys have not been regenerated from the "
                "Dashboard. Regenerating a key invalidates the old one immediately."
            ),
            "language": "python",
            "upvotes": 35,
            "contributed_by": "system",
        },
        {
            "id": "rzp-003",
            "library_id": "/razorpay/razorpay-sdk",
            "error_code": "WEBHOOK_SIGNATURE_MISMATCH",
            "error_message": "razorpay.errors.SignatureVerificationError: Webhook signature verification failed",
            "solution": (
                "The webhook signature is computed from the raw request body + "
                "webhook secret (not API key secret). Common causes:\n"
                "1. Using API key secret instead of webhook secret\n"
                "2. Parsing/modifying the request body before verification\n"
                "3. Incorrect secret from Dashboard > Settings > Webhooks\n\n"
                "```python\n"
                "import razorpay\n\n"
                "client = razorpay.Client(auth=('key_id', 'key_secret'))\n\n"
                "# Use the RAW request body, not parsed JSON\n"
                "webhook_body = request.body  # raw bytes/string\n"
                "webhook_signature = request.headers.get('X-Razorpay-Signature')\n"
                "webhook_secret = os.environ['RAZORPAY_WEBHOOK_SECRET']  # NOT api key secret\n\n"
                "try:\n"
                "    client.utility.verify_webhook_signature(\n"
                "        webhook_body, webhook_signature, webhook_secret\n"
                "    )\n"
                "except razorpay.errors.SignatureVerificationError:\n"
                "    return HttpResponse(status=400)\n"
                "```"
            ),
            "language": "python",
            "upvotes": 52,
            "contributed_by": "system",
        },
        {
            "id": "rzp-004",
            "library_id": "/razorpay/razorpay-sdk",
            "error_code": "BAD_REQUEST_ERROR",
            "error_message": "The payment has already been captured",
            "solution": (
                "Razorpay payments auto-capture if `capture` is set in the "
                "order or if auto-capture is enabled in Dashboard settings. "
                "Calling capture on an already-captured payment throws this "
                "error.\n\n"
                "```python\n"
                "# Check payment status before capturing\n"
                "payment = client.payment.fetch(payment_id)\n"
                "if payment['status'] == 'authorized':\n"
                "    client.payment.capture(payment_id, payment['amount'])\n"
                "elif payment['status'] == 'captured':\n"
                "    print('Already captured, no action needed')\n"
                "```\n\n"
                "If you want manual capture: create orders with "
                "`payment.capture: 'manual'` or disable auto-capture in "
                "Dashboard > Settings > Payments."
            ),
            "language": "python",
            "upvotes": 28,
            "contributed_by": "system",
        },
    ],
    "cashfree": [
        {
            "id": "cf-001",
            "library_id": "/cashfree/cashfree-pg",
            "error_code": "ORDER_CREATION_FAILED",
            "error_message": "order_amount must be greater than or equal to 1.00",
            "solution": (
                "Cashfree expects amount in rupees (not paise, unlike Razorpay). "
                "Minimum order amount is INR 1.00.\n\n"
                "```python\n"
                "from cashfree_pg.models import CreateOrderRequest\n\n"
                "# Cashfree uses rupees, not paise\n"
                "order = CreateOrderRequest(\n"
                "    order_amount=500.00,  # INR 500 (not paise!)\n"
                "    order_currency='INR',\n"
                "    customer_details=customer,\n"
                "    order_id='order_' + str(uuid.uuid4())[:8]\n"
                ")\n"
                "```\n\n"
                "Note: This is a common source of bugs when migrating from "
                "Razorpay (paise) to Cashfree (rupees)."
            ),
            "language": "python",
            "upvotes": 22,
            "contributed_by": "system",
        },
        {
            "id": "cf-002",
            "library_id": "/cashfree/cashfree-pg",
            "error_code": "SETTLEMENT_DELAY",
            "error_message": "Settlement status: ON_HOLD — KYC verification pending",
            "solution": (
                "Cashfree holds settlements until merchant KYC is complete. "
                "This is common for new accounts.\n\n"
                "Steps to resolve:\n"
                "1. Login to Cashfree Dashboard > Account > KYC\n"
                "2. Upload PAN card, cancelled cheque, business registration\n"
                "3. Verification takes 1-2 business days\n"
                "4. After KYC approval, settlement cycle: T+2 for PG, T+1 for payouts\n\n"
                "For testing: use sandbox mode (sandbox.cashfree.com) which "
                "does not require KYC and simulates settlements instantly."
            ),
            "language": "python",
            "upvotes": 15,
            "contributed_by": "system",
        },
    ],
    "zerodha": [
        {
            "id": "zrd-001",
            "library_id": "/zerodha/kite-api",
            "error_code": "TokenException",
            "error_message": "kiteconnect.exceptions.TokenException: Token is invalid or has expired",
            "solution": (
                "Kite Connect access tokens expire at 6 AM IST daily (market "
                "opening time). You must regenerate the token every day.\n\n"
                "```python\n"
                "from kiteconnect import KiteConnect\n\n"
                "kite = KiteConnect(api_key='your_api_key')\n\n"
                "# Step 1: Generate login URL (do this once per day)\n"
                "login_url = kite.login_url()\n"
                "# User logs in → redirect gives you request_token\n\n"
                "# Step 2: Exchange request_token for access_token\n"
                "data = kite.generate_session(\n"
                "    request_token='token_from_redirect',\n"
                "    api_secret='your_api_secret'\n"
                ")\n"
                "access_token = data['access_token']\n"
                "kite.set_access_token(access_token)\n\n"
                "# Step 3: Store access_token, reuse until 6 AM next day\n"
                "# Implement automatic refresh in your cron job\n"
                "```\n\n"
                "For algo trading: automate the login flow using Selenium or "
                "kite.trade's TOTP-based login."
            ),
            "language": "python",
            "upvotes": 63,
            "contributed_by": "system",
        },
        {
            "id": "zrd-002",
            "library_id": "/zerodha/kite-api",
            "error_code": "NetworkException",
            "error_message": "kiteconnect.exceptions.NetworkException: Gateway timed out",
            "solution": (
                "Kite API can be slow during market open (9:15 AM IST) and "
                "close (3:30 PM IST) due to high load. Also happens with "
                "WebSocket disconnections.\n\n"
                "```python\n"
                "from kiteconnect import KiteConnect\n"
                "import time\n\n"
                "def place_order_with_retry(kite, params, max_retries=3):\n"
                "    for attempt in range(max_retries):\n"
                "        try:\n"
                "            return kite.place_order(**params)\n"
                "        except kite.exceptions.NetworkException:\n"
                "            if attempt < max_retries - 1:\n"
                "                time.sleep(2 ** attempt)  # Exponential backoff\n"
                "            else:\n"
                "                raise\n"
                "```\n\n"
                "For WebSocket: implement auto-reconnect with on_close callback. "
                "Kite WebSocket has a 5-second ping interval; if 3 pings are "
                "missed, connection drops."
            ),
            "language": "python",
            "upvotes": 41,
            "contributed_by": "system",
        },
        {
            "id": "zrd-003",
            "library_id": "/zerodha/kite-api",
            "error_code": "OrderException",
            "error_message": "kiteconnect.exceptions.InputException: Order rejected — Insufficient margins",
            "solution": (
                "The order requires more margin than available in your account. "
                "Check available margins before placing orders.\n\n"
                "```python\n"
                "# Check margins before placing order\n"
                "margins = kite.margins()\n"
                "available = margins['equity']['available']['live_balance']\n"
                "print(f'Available margin: INR {available}')\n\n"
                "# For F&O, check derivative margins\n"
                "f_and_o = margins.get('commodity', {}).get('available', {})\n"
                "```\n\n"
                "Common margin rejection codes:\n"
                "- 'Insufficient margins': need more funds\n"
                "- 'Order exceeds the current freeze quantity': reduce quantity\n"
                "- 'Market is closed': check NSE/BSE trading hours (9:15-15:30 IST)"
            ),
            "language": "python",
            "upvotes": 38,
            "contributed_by": "system",
        },
    ],
    "gstn": [
        {
            "id": "gst-001",
            "library_id": "/gstn/gst-api",
            "error_code": "INVALID_GSTIN",
            "error_message": "Invalid GSTIN format. GSTIN must be a valid 15-character alphanumeric string.",
            "solution": (
                "GSTIN format: 2-digit state code + 10-char PAN + 1 entity "
                "number + 1Z + 1 checksum.\n\n"
                "```python\n"
                "import re\n\n"
                "GSTIN_REGEX = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'\n\n"
                "def validate_gstin(gstin: str) -> bool:\n"
                "    if not re.match(GSTIN_REGEX, gstin):\n"
                "        return False\n"
                "    # State code must be 01-37 (valid Indian state codes)\n"
                "    state_code = int(gstin[:2])\n"
                "    return 1 <= state_code <= 37\n\n"
                "# Example valid GSTINs\n"
                "assert validate_gstin('27AAPFU0939F1ZV')  # Maharashtra\n"
                "assert validate_gstin('29GGGGG1314R9Z6')  # Karnataka\n"
                "```\n\n"
                "Always validate client-side before making API calls to avoid "
                "unnecessary rate limit consumption."
            ),
            "language": "python",
            "upvotes": 31,
            "contributed_by": "system",
        },
        {
            "id": "gst-002",
            "library_id": "/gstn/gst-api",
            "error_code": "RATE_LIMIT_EXCEEDED",
            "error_message": "Too many requests. Rate limit: 10 requests per minute per GSTIN.",
            "solution": (
                "GSTN enforces strict rate limits. Exceeding them can result "
                "in a 24-hour IP block.\n\n"
                "```python\n"
                "import time\n"
                "from collections import defaultdict\n\n"
                "class GSTNRateLimiter:\n"
                "    def __init__(self, max_per_minute: int = 10):\n"
                "        self.max_per_minute = max_per_minute\n"
                "        self._timestamps: dict[str, list[float]] = defaultdict(list)\n\n"
                "    def wait_if_needed(self, gstin: str) -> None:\n"
                "        now = time.time()\n"
                "        window = [t for t in self._timestamps[gstin] if now - t < 60]\n"
                "        self._timestamps[gstin] = window\n"
                "        if len(window) >= self.max_per_minute:\n"
                "            sleep_time = 60 - (now - window[0])\n"
                "            time.sleep(sleep_time)\n"
                "        self._timestamps[gstin].append(time.time())\n"
                "```\n\n"
                "For batch operations (filing returns for multiple GSTINs), "
                "use a task queue (Celery) and process sequentially with delays."
            ),
            "language": "python",
            "upvotes": 24,
            "contributed_by": "system",
        },
        {
            "id": "gst-003",
            "library_id": "/gstn/gst-api",
            "error_code": "SESSION_EXPIRED",
            "error_message": "Auth token expired. Please re-authenticate.",
            "solution": (
                "GSTN sessions are OTP-based and expire after 6 hours. You "
                "cannot refresh — must re-authenticate with a new OTP.\n\n"
                "```python\n"
                "import time\n\n"
                "class GSTNSession:\n"
                "    def __init__(self):\n"
                "        self.token = None\n"
                "        self.expires_at = 0\n\n"
                "    @property\n"
                "    def is_expired(self) -> bool:\n"
                "        return time.time() > self.expires_at - 300  # 5 min buffer\n\n"
                "    def authenticate(self, gstin: str, otp: str) -> str:\n"
                "        # POST /authenticate with GSTIN + OTP\n"
                "        response = gstn_api.authenticate(gstin, otp)\n"
                "        self.token = response['auth_token']\n"
                "        self.expires_at = time.time() + (6 * 3600)  # 6 hours\n"
                "        return self.token\n"
                "```\n\n"
                "For automated systems: implement a callback mechanism that "
                "pauses operations and requests a new OTP when session expires."
            ),
            "language": "python",
            "upvotes": 19,
            "contributed_by": "system",
        },
    ],
    "upi": [
        {
            "id": "upi-001",
            "library_id": "/npci/upi-specs",
            "error_code": "COLLECT_TIMEOUT",
            "error_message": "Transaction status: EXPIRED — Collect request timed out after 5 minutes",
            "solution": (
                "UPI collect requests have a 5-minute expiry by default (some "
                "PSP banks allow up to 30 minutes).\n\n"
                "```python\n"
                "import asyncio\n\n"
                "async def wait_for_upi_payment(\n"
                "    txn_id: str,\n"
                "    timeout_seconds: int = 300,\n"
                "    poll_interval: int = 10\n"
                ") -> dict:\n"
                "    \"\"\"Poll for UPI payment status with timeout.\"\"\"\n"
                "    elapsed = 0\n"
                "    while elapsed < timeout_seconds:\n"
                "        status = await check_transaction_status(txn_id)\n"
                "        if status['state'] in ('SUCCESS', 'FAILURE', 'EXPIRED'):\n"
                "            return status\n"
                "        await asyncio.sleep(poll_interval)\n"
                "        elapsed += poll_interval\n"
                "    return {'state': 'EXPIRED', 'txn_id': txn_id}\n"
                "```\n\n"
                "UI best practice: show a countdown timer and prompt the user "
                "to check their UPI app. Offer retry via a new collect request "
                "if the first one expires."
            ),
            "language": "python",
            "upvotes": 33,
            "contributed_by": "system",
        },
        {
            "id": "upi-002",
            "library_id": "/npci/upi-specs",
            "error_code": "MANDATE_REGISTRATION_FAILED",
            "error_message": "Mandate registration declined by payer PSP",
            "solution": (
                "UPI mandate (autopay) registration can fail for several reasons:\n\n"
                "1. **Payer's bank does not support mandates**: Not all banks support "
                "UPI 2.0 mandates. Check NPCI's mandate-supported banks list.\n"
                "2. **Incorrect mandate parameters**: frequency, start_date, "
                "end_date, and amount must all be valid.\n"
                "3. **Payer declined on their UPI app**: User rejected the mandate.\n\n"
                "```python\n"
                "mandate_params = {\n"
                "    'payer_vpa': 'user@upi',\n"
                "    'payee_vpa': 'merchant@ybl',\n"
                "    'amount': '999.00',\n"
                "    'frequency': 'MONTHLY',  # DAILY, WEEKLY, MONTHLY, YEARLY\n"
                "    'start_date': '2026-04-01',\n"
                "    'end_date': '2027-03-31',\n"
                "    'mandate_type': 'CREATE',\n"
                "}\n"
                "```\n\n"
                "Always provide clear mandate details to the user before they "
                "approve on their UPI app. Vague descriptions increase rejection rates."
            ),
            "language": "python",
            "upvotes": 26,
            "contributed_by": "system",
        },
    ],
    "ondc": [
        {
            "id": "ondc-001",
            "library_id": "/ondc/protocol-specs",
            "error_code": "SIGNING_ERROR",
            "error_message": "Authorization header validation failed: Invalid signature",
            "solution": (
                "ONDC requires Ed25519 signing (not RSA). The most common "
                "errors are: wrong key type, incorrect digest computation, "
                "or timestamp mismatch.\n\n"
                "```python\n"
                "import base64\n"
                "import hashlib\n"
                "import time\n"
                "from nacl.signing import SigningKey\n\n"
                "def sign_ondc_request(body: str, private_key_b64: str,\n"
                "                      subscriber_id: str, key_id: str) -> str:\n"
                "    \"\"\"Generate ONDC Beckn Authorization header.\"\"\"\n"
                "    # Compute Blake2b-512 digest of body\n"
                "    digest = hashlib.blake2b(body.encode(), digest_size=64).digest()\n"
                "    digest_b64 = base64.b64encode(digest).decode()\n\n"
                "    created = int(time.time())\n"
                "    expires = created + 300  # 5-minute validity\n\n"
                "    signing_string = (\n"
                "        f'(created): {created}\\n'\n"
                "        f'(expires): {expires}\\n'\n"
                "        f'digest: BLAKE-512={digest_b64}'\n"
                "    )\n\n"
                "    private_key = SigningKey(base64.b64decode(private_key_b64))\n"
                "    signed = private_key.sign(signing_string.encode())\n"
                "    signature = base64.b64encode(signed.signature).decode()\n\n"
                "    return (\n"
                "        f'Signature keyId=\"{subscriber_id}|{key_id}|ed25519\",'\n"
                "        f'algorithm=\"ed25519\",created=\"{created}\",'\n"
                "        f'expires=\"{expires}\",'\n"
                "        f'headers=\"(created) (expires) digest\",'\n"
                "        f'signature=\"{signature}\"'\n"
                "    )\n"
                "```\n\n"
                "Install: `pip install PyNaCl`. Key must be the raw 32-byte "
                "Ed25519 seed, base64-encoded."
            ),
            "language": "python",
            "upvotes": 44,
            "contributed_by": "system",
        },
        {
            "id": "ondc-002",
            "library_id": "/ondc/protocol-specs",
            "error_code": "REGISTRY_LOOKUP_FAILED",
            "error_message": "Unable to find subscriber in ONDC registry",
            "solution": (
                "Registry lookup failures happen when:\n"
                "1. Subscriber is not registered on the correct environment\n"
                "2. Subscriber's signing key doesn't match registry entry\n"
                "3. Subscriber URL has changed but registry is not updated\n\n"
                "```python\n"
                "import httpx\n\n"
                "ONDC_REGISTRY = {\n"
                "    'staging': 'https://staging.registry.ondc.org/lookup',\n"
                "    'production': 'https://registry.ondc.org/lookup'\n"
                "}\n\n"
                "async def lookup_subscriber(subscriber_id: str,\n"
                "                            env: str = 'staging') -> dict:\n"
                "    async with httpx.AsyncClient() as client:\n"
                "        response = await client.post(\n"
                "            ONDC_REGISTRY[env],\n"
                "            json={'subscriber_id': subscriber_id}\n"
                "        )\n"
                "        if response.status_code != 200:\n"
                "            raise ValueError(\n"
                "                f'Registry lookup failed for {subscriber_id}: '\n"
                "                f'{response.status_code}'\n"
                "            )\n"
                "        return response.json()\n"
                "```\n\n"
                "Verify: your subscriber_id in API requests matches exactly "
                "what was registered (case-sensitive, no trailing slash)."
            ),
            "language": "python",
            "upvotes": 37,
            "contributed_by": "system",
        },
        {
            "id": "ondc-003",
            "library_id": "/ondc/protocol-specs",
            "error_code": "SCHEMA_VALIDATION_ERROR",
            "error_message": "Request body does not conform to ONDC schema v1.2.0",
            "solution": (
                "ONDC validates all API payloads against strict JSON schemas. "
                "Use the official log validation utility to check your payloads "
                "before sending.\n\n"
                "```bash\n"
                "# Clone the validation utility\n"
                "git clone https://github.com/ONDC-Official/log-validation-utility\n"
                "cd log-validation-utility\n"
                "npm install\n\n"
                "# Validate your API logs\n"
                "npm run validate -- --domain retail --flow search\n"
                "```\n\n"
                "Common schema violations:\n"
                "- Missing `context.message_id` (must be unique UUID per request)\n"
                "- Incorrect `context.timestamp` format (must be ISO 8601 with timezone)\n"
                "- Missing required fields in `message.intent` for /search\n"
                "- `item.price.value` must be string, not number"
            ),
            "language": "javascript",
            "upvotes": 29,
            "contributed_by": "system",
        },
    ],
}

# Map library IDs to error data keys
_LIBRARY_ERROR_MAP: dict[str, str] = {
    "/razorpay/razorpay-sdk": "razorpay",
    "/razorpay": "razorpay",
    "razorpay": "razorpay",
    "/cashfree/cashfree-pg": "cashfree",
    "/cashfree": "cashfree",
    "cashfree": "cashfree",
    "/zerodha/kite-api": "zerodha",
    "/zerodha": "zerodha",
    "zerodha": "zerodha",
    "/gstn/gst-api": "gstn",
    "/gstn": "gstn",
    "gstn": "gstn",
    "/npci/upi-specs": "upi",
    "/npci/upi": "upi",
    "upi": "upi",
    "/ondc/protocol-specs": "ondc",
    "/ondc": "ondc",
    "ondc": "ondc",
}

# Community-contributed patterns stored in memory for MVP
_community_patterns: list[dict] = []


# ── Endpoints ────────────────────────────────────────────────────


@router.get("/{library_id:path}", response_model=ErrorPatternListResponse)
async def get_error_patterns(library_id: str) -> ErrorPatternListResponse:
    """
    Get common errors and fixes for a library.

    Returns pre-populated error patterns for Indian API integrations,
    including community-contributed patterns. Each pattern includes
    the error code, message, and a step-by-step solution with code.

    Args:
        library_id: Canonical library ID or short name (e.g. "razorpay",
                    "/zerodha/kite-api", "ondc").
    """
    if not flags.ERROR_PATTERNS:
        raise HTTPException(
            status_code=403,
            detail="Error patterns feature is disabled. Set FEATURE_ERROR_PATTERNS=true to enable.",
        )

    normalized = library_id.strip().lower()
    data_key = _LIBRARY_ERROR_MAP.get(normalized) or _LIBRARY_ERROR_MAP.get(
        f"/{normalized}"
    )

    if data_key is None:
        last_segment = normalized.rstrip("/").rsplit("/", 1)[-1]
        data_key = _LIBRARY_ERROR_MAP.get(last_segment)

    if data_key is None or data_key not in _ERROR_PATTERNS:
        available = sorted({v for v in _LIBRARY_ERROR_MAP.values()})
        raise HTTPException(
            status_code=404,
            detail=(
                f"No error patterns found for '{library_id}'. "
                f"Available: {', '.join(available)}"
            ),
        )

    # Merge system patterns with community contributions for this library
    system_patterns = _ERROR_PATTERNS[data_key]
    community = [
        p for p in _community_patterns if p.get("_data_key") == data_key
    ]

    all_patterns = system_patterns + community
    logger.info(
        "Serving error patterns",
        extra={
            "library_id": library_id,
            "resolved_key": data_key,
            "system_count": len(system_patterns),
            "community_count": len(community),
        },
    )

    return ErrorPatternListResponse(
        library_id=library_id,
        patterns=[ErrorPattern(**{k: v for k, v in p.items() if k != "_data_key"}) for p in all_patterns],
        total=len(all_patterns),
    )


@router.post("", response_model=SubmitErrorPatternResponse)
async def submit_error_pattern(
    request: SubmitErrorPatternRequest,
) -> SubmitErrorPatternResponse:
    """
    Submit a new community-contributed error pattern.

    Community contributions are stored in memory for MVP. In production,
    these would be persisted to the database and go through a moderation
    queue before being publicly visible.

    Args:
        request: The error pattern details including library ID, error code,
                error message, solution, and programming language.
    """
    if not flags.ERROR_PATTERNS:
        raise HTTPException(
            status_code=403,
            detail="Error patterns feature is disabled. Set FEATURE_ERROR_PATTERNS=true to enable.",
        )

    pattern_id = f"community-{uuid.uuid4().hex[:8]}"

    # Resolve data key for grouping
    normalized = request.library_id.strip().lower()
    data_key = _LIBRARY_ERROR_MAP.get(normalized, normalized)

    pattern = {
        "id": pattern_id,
        "library_id": request.library_id,
        "error_code": request.error_code,
        "error_message": request.error_message,
        "solution": request.solution,
        "language": request.language,
        "upvotes": 0,
        "contributed_by": "community",
        "_data_key": data_key,
    }
    _community_patterns.append(pattern)

    logger.info(
        "Community error pattern submitted",
        extra={
            "pattern_id": pattern_id,
            "library_id": request.library_id,
            "error_code": request.error_code,
        },
    )

    return SubmitErrorPatternResponse(
        id=pattern_id,
        library_id=request.library_id,
        error_code=request.error_code,
        submitted=True,
    )
