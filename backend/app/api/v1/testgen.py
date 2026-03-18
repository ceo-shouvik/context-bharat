"""Test scaffolding generation — generates integration test templates from API docs."""
from __future__ import annotations

import logging
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tests", tags=["test-generation"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class TestLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"


class TestFramework(str, Enum):
    PYTEST = "pytest"
    JEST = "jest"
    MOCHA = "mocha"


class GenerateTestRequest(BaseModel):
    library_id: str = Field(..., description="ContextBharat library ID")
    language: TestLanguage = Field(default=TestLanguage.PYTHON)
    framework: TestFramework | None = Field(
        default=None,
        description="Test framework. Defaults to pytest for Python, jest for JavaScript.",
    )


class GenerateTestResponse(BaseModel):
    test_code: str
    framework: str
    test_count: int
    explanation: str


# ─── Test Templates ──────────────────────────────────────────────────────────

def _get_lib_name(library_id: str) -> str:
    parts = library_id.strip("/").split("/")
    return parts[-1].replace("-", "_") if parts else "api"


PYTHON_PYTEST_TEMPLATES: dict[str, str] = {
    "/razorpay/razorpay-sdk": '''"""Integration tests for Razorpay SDK."""
import os
import pytest
import razorpay


@pytest.fixture
def client():
    """Create a Razorpay test client."""
    key_id = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_XXXX")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET", "secret_XXXX")
    return razorpay.Client(auth=(key_id, key_secret))


class TestOrderCreation:
    """Test Razorpay order creation flow."""

    def test_create_order_success(self, client):
        """Should create an order with valid amount and currency."""
        order = client.order.create({
            "amount": 50000,
            "currency": "INR",
            "receipt": "test_receipt_001",
            "payment_capture": 1,
        })
        assert order["id"].startswith("order_")
        assert order["amount"] == 50000
        assert order["currency"] == "INR"
        assert order["status"] == "created"

    def test_create_order_invalid_amount(self, client):
        """Should reject order with zero amount."""
        with pytest.raises(razorpay.errors.BadRequestError):
            client.order.create({
                "amount": 0,
                "currency": "INR",
                "receipt": "test_receipt_002",
            })

    def test_create_order_invalid_currency(self, client):
        """Should reject order with unsupported currency."""
        with pytest.raises(razorpay.errors.BadRequestError):
            client.order.create({
                "amount": 50000,
                "currency": "INVALID",
                "receipt": "test_receipt_003",
            })

    def test_fetch_order(self, client):
        """Should fetch a created order by ID."""
        order = client.order.create({
            "amount": 10000,
            "currency": "INR",
            "receipt": "test_fetch_001",
        })
        fetched = client.order.fetch(order["id"])
        assert fetched["id"] == order["id"]
        assert fetched["amount"] == 10000


class TestPaymentLink:
    """Test Razorpay payment link creation."""

    def test_create_payment_link(self, client):
        """Should create a payment link with customer details."""
        link = client.payment_link.create({
            "amount": 25000,
            "currency": "INR",
            "description": "Test Payment",
            "customer": {
                "name": "Test Customer",
                "email": "test@example.com",
                "contact": "+919876543210",
            },
            "notify": {"sms": False, "email": False},
        })
        assert "short_url" in link
        assert link["amount"] == 25000

    def test_payment_link_with_callback(self, client):
        """Should create payment link with callback URL."""
        link = client.payment_link.create({
            "amount": 15000,
            "currency": "INR",
            "description": "Test Callback",
            "callback_url": "https://example.com/callback",
            "callback_method": "get",
        })
        assert link["callback_url"] == "https://example.com/callback"


class TestWebhookSignature:
    """Test Razorpay webhook signature verification."""

    def test_valid_signature(self, client):
        """Should verify a valid webhook signature."""
        import hmac
        import hashlib

        body = b\'{"event":"payment.captured","payload":{}}\'
        secret = "webhook_secret_test"
        expected_sig = hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()

        # Verify the signature matches
        computed = hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        assert computed == expected_sig

    def test_invalid_signature_rejected(self):
        """Should reject an invalid webhook signature."""
        import hmac
        import hashlib

        body = b\'{"event":"payment.captured"}\'
        correct_sig = hmac.new(b"correct_secret", body, hashlib.sha256).hexdigest()
        wrong_sig = hmac.new(b"wrong_secret", body, hashlib.sha256).hexdigest()
        assert correct_sig != wrong_sig
''',
    "/zerodha/kite-api": '''"""Integration tests for Zerodha Kite Connect API."""
import os
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def kite():
    """Create a mock Kite Connect client for testing."""
    from kiteconnect import KiteConnect
    client = KiteConnect(api_key="test_api_key")
    client.set_access_token("test_access_token")
    return client


class TestAuthentication:
    """Test Kite Connect authentication flow."""

    def test_login_url_generation(self):
        """Should generate a valid login URL."""
        from kiteconnect import KiteConnect
        kite = KiteConnect(api_key="test_key")
        url = kite.login_url()
        assert "test_key" in url
        assert "kite.zerodha.com" in url

    @patch("kiteconnect.KiteConnect._post")
    def test_generate_session(self, mock_post):
        """Should exchange request_token for access_token."""
        from kiteconnect import KiteConnect
        mock_post.return_value = {
            "access_token": "mock_access_token",
            "user_id": "AB1234",
        }
        kite = KiteConnect(api_key="test_key")
        data = kite.generate_session("test_request_token", api_secret="test_secret")
        assert "access_token" in data


class TestOrderPlacement:
    """Test order placement via Kite API."""

    @patch("kiteconnect.KiteConnect._post")
    def test_place_market_order(self, mock_post, kite):
        """Should place a market order successfully."""
        mock_post.return_value = {"order_id": "123456789"}
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol="INFY",
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=1,
            order_type=kite.ORDER_TYPE_MARKET,
            product=kite.PRODUCT_CNC,
        )
        assert order_id is not None

    @patch("kiteconnect.KiteConnect._post")
    def test_place_limit_order(self, mock_post, kite):
        """Should place a limit order with price."""
        mock_post.return_value = {"order_id": "123456790"}
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol="RELIANCE",
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=5,
            order_type=kite.ORDER_TYPE_LIMIT,
            product=kite.PRODUCT_CNC,
            price=2500.00,
        )
        assert order_id is not None


class TestPortfolio:
    """Test portfolio-related endpoints."""

    @patch("kiteconnect.KiteConnect._get")
    def test_get_holdings(self, mock_get, kite):
        """Should return portfolio holdings."""
        mock_get.return_value = [
            {"tradingsymbol": "INFY", "quantity": 10, "average_price": 1500.0},
            {"tradingsymbol": "TCS", "quantity": 5, "average_price": 3500.0},
        ]
        holdings = kite.holdings()
        assert len(holdings) == 2
        assert holdings[0]["tradingsymbol"] == "INFY"

    @patch("kiteconnect.KiteConnect._get")
    def test_get_positions(self, mock_get, kite):
        """Should return open positions."""
        mock_get.return_value = {
            "net": [{"tradingsymbol": "NIFTY24MARFUT", "quantity": 50, "pnl": 1200.0}],
            "day": [],
        }
        positions = kite.positions()
        assert "net" in positions
        assert len(positions["net"]) == 1
''',
}

JS_JEST_TEMPLATES: dict[str, str] = {
    "/razorpay/razorpay-sdk": '''/**
 * Integration tests for Razorpay Node.js SDK.
 * Run: npx jest razorpay.test.js
 */
const Razorpay = require("razorpay");
const crypto = require("crypto");

const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID || "rzp_test_XXXX",
  key_secret: process.env.RAZORPAY_KEY_SECRET || "secret_XXXX",
});

describe("Razorpay Orders", () => {
  let orderId;

  test("should create an order with valid params", async () => {
    const order = await razorpay.orders.create({
      amount: 50000,
      currency: "INR",
      receipt: "test_order_001",
    });
    expect(order.id).toMatch(/^order_/);
    expect(order.amount).toBe(50000);
    expect(order.currency).toBe("INR");
    expect(order.status).toBe("created");
    orderId = order.id;
  });

  test("should fetch a created order", async () => {
    if (!orderId) return;
    const order = await razorpay.orders.fetch(orderId);
    expect(order.id).toBe(orderId);
  });

  test("should reject order with invalid amount", async () => {
    await expect(
      razorpay.orders.create({ amount: 0, currency: "INR", receipt: "bad" })
    ).rejects.toThrow();
  });
});

describe("Razorpay Payment Links", () => {
  test("should create a payment link", async () => {
    const link = await razorpay.paymentLink.create({
      amount: 25000,
      currency: "INR",
      description: "Test Payment Link",
      customer: {
        name: "Test User",
        email: "test@example.com",
        contact: "+919876543210",
      },
      notify: { sms: false, email: false },
    });
    expect(link.short_url).toBeDefined();
    expect(link.amount).toBe(25000);
  });
});

describe("Webhook Signature Verification", () => {
  test("should verify valid signature", () => {
    const body = JSON.stringify({ event: "payment.captured" });
    const secret = "test_webhook_secret";
    const signature = crypto
      .createHmac("sha256", secret)
      .update(body)
      .digest("hex");

    const verified = crypto
      .createHmac("sha256", secret)
      .update(body)
      .digest("hex");

    expect(verified).toBe(signature);
  });

  test("should reject invalid signature", () => {
    const body = JSON.stringify({ event: "payment.captured" });
    const correct = crypto.createHmac("sha256", "correct").update(body).digest("hex");
    const wrong = crypto.createHmac("sha256", "wrong").update(body).digest("hex");
    expect(correct).not.toBe(wrong);
  });
});
''',
}

JS_MOCHA_TEMPLATES: dict[str, str] = {
    "/razorpay/razorpay-sdk": '''/**
 * Integration tests for Razorpay Node.js SDK (Mocha + Chai).
 * Run: npx mocha razorpay.test.js
 */
const { expect } = require("chai");
const Razorpay = require("razorpay");
const crypto = require("crypto");

const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID || "rzp_test_XXXX",
  key_secret: process.env.RAZORPAY_KEY_SECRET || "secret_XXXX",
});

describe("Razorpay Orders", function () {
  this.timeout(10000);
  let orderId;

  it("should create an order with valid params", async () => {
    const order = await razorpay.orders.create({
      amount: 50000,
      currency: "INR",
      receipt: "test_order_mocha_001",
    });
    expect(order.id).to.match(/^order_/);
    expect(order.amount).to.equal(50000);
    expect(order.status).to.equal("created");
    orderId = order.id;
  });

  it("should fetch a created order", async () => {
    if (!orderId) return;
    const order = await razorpay.orders.fetch(orderId);
    expect(order.id).to.equal(orderId);
  });

  it("should reject order with zero amount", async () => {
    try {
      await razorpay.orders.create({ amount: 0, currency: "INR", receipt: "bad" });
      expect.fail("Should have thrown");
    } catch (err) {
      expect(err).to.exist;
    }
  });
});

describe("Webhook Signature", () => {
  it("should verify a valid signature", () => {
    const body = JSON.stringify({ event: "payment.captured" });
    const secret = "test_secret";
    const sig = crypto.createHmac("sha256", secret).update(body).digest("hex");
    const verified = crypto.createHmac("sha256", secret).update(body).digest("hex");
    expect(verified).to.equal(sig);
  });
});
''',
}


def _default_pytest(library_id: str) -> str:
    lib_name = _get_lib_name(library_id)
    return f'''"""Integration tests for {library_id}."""
import os
import pytest


# TODO: Configure the client for {library_id}
# Install SDK: pip install {lib_name}

@pytest.fixture
def client():
    """Create an API client for {library_id}."""
    api_key = os.environ.get("{lib_name.upper()}_API_KEY", "test_key")
    # TODO: Replace with actual SDK client initialization
    return {{"api_key": api_key}}


class TestAuthentication:
    """Test API authentication."""

    def test_valid_api_key(self, client):
        """Should authenticate with a valid API key."""
        assert client["api_key"] is not None

    def test_invalid_api_key_rejected(self):
        """Should reject invalid API keys."""
        # TODO: Test with invalid credentials
        pass


class TestCoreEndpoints:
    """Test core API endpoints for {library_id}."""

    def test_list_resources(self, client):
        """Should list available resources."""
        # TODO: Replace with actual API call
        # response = client.resources.list()
        # assert isinstance(response, list)
        pass

    def test_create_resource(self, client):
        """Should create a new resource."""
        # TODO: Replace with actual API call
        # resource = client.resources.create({{...}})
        # assert resource["id"] is not None
        pass

    def test_get_resource_by_id(self, client):
        """Should fetch a resource by ID."""
        # TODO: Replace with actual API call
        pass

    def test_update_resource(self, client):
        """Should update an existing resource."""
        # TODO: Replace with actual API call
        pass

    def test_delete_resource(self, client):
        """Should delete a resource."""
        # TODO: Replace with actual API call
        pass


class TestErrorHandling:
    """Test error handling for {library_id}."""

    def test_not_found_returns_404(self, client):
        """Should return 404 for non-existent resources."""
        # TODO: Test with non-existent ID
        pass

    def test_invalid_input_returns_400(self, client):
        """Should return 400 for invalid input."""
        # TODO: Test with invalid data
        pass

    def test_rate_limit_handling(self, client):
        """Should handle rate limits gracefully."""
        # TODO: Test rate limit behavior
        pass
'''


def _default_jest(library_id: str) -> str:
    lib_name = _get_lib_name(library_id)
    return f'''/**
 * Integration tests for {library_id}.
 * Run: npx jest {lib_name}.test.js
 */

// TODO: Import the SDK
// const Client = require("{lib_name}");

describe("{lib_name} API", () => {{
  let client;

  beforeAll(() => {{
    const apiKey = process.env.{lib_name.upper()}_API_KEY || "test_key";
    // TODO: Initialize client
    client = {{ apiKey }};
  }});

  describe("Authentication", () => {{
    test("should authenticate with valid API key", () => {{
      expect(client.apiKey).toBeDefined();
    }});
  }});

  describe("Core Endpoints", () => {{
    test("should list resources", async () => {{
      // TODO: Replace with actual API call
      // const resources = await client.resources.list();
      // expect(Array.isArray(resources)).toBe(true);
    }});

    test("should create a resource", async () => {{
      // TODO: Replace with actual API call
      // const resource = await client.resources.create({{...}});
      // expect(resource.id).toBeDefined();
    }});

    test("should fetch a resource by ID", async () => {{
      // TODO: Replace with actual API call
    }});

    test("should update a resource", async () => {{
      // TODO: Replace with actual API call
    }});

    test("should delete a resource", async () => {{
      // TODO: Replace with actual API call
    }});
  }});

  describe("Error Handling", () => {{
    test("should throw on invalid input", async () => {{
      // TODO: Test error handling
    }});

    test("should handle rate limits", async () => {{
      // TODO: Test rate limit behavior
    }});
  }});
}});
'''


def _default_mocha(library_id: str) -> str:
    lib_name = _get_lib_name(library_id)
    return f'''/**
 * Integration tests for {library_id} (Mocha + Chai).
 * Run: npx mocha {lib_name}.test.js
 */
const {{ expect }} = require("chai");

// TODO: Import the SDK
// const Client = require("{lib_name}");

describe("{lib_name} API", function () {{
  this.timeout(10000);
  let client;

  before(() => {{
    const apiKey = process.env.{lib_name.upper()}_API_KEY || "test_key";
    // TODO: Initialize client
    client = {{ apiKey }};
  }});

  describe("Authentication", () => {{
    it("should authenticate with valid API key", () => {{
      expect(client.apiKey).to.exist;
    }});
  }});

  describe("Core Endpoints", () => {{
    it("should list resources", async () => {{
      // TODO: Replace with actual API call
    }});

    it("should create a resource", async () => {{
      // TODO: Replace with actual API call
    }});
  }});

  describe("Error Handling", () => {{
    it("should throw on invalid input", async () => {{
      // TODO: Test error handling
    }});
  }});
}});
'''


def _resolve_framework(
    language: TestLanguage,
    framework: TestFramework | None,
) -> TestFramework:
    """Resolve default framework based on language."""
    if framework is not None:
        return framework
    return TestFramework.PYTEST if language == TestLanguage.PYTHON else TestFramework.JEST


def _generate_tests(
    library_id: str,
    language: TestLanguage,
    framework: TestFramework,
) -> tuple[str, int]:
    """Generate test code and return (code, test_count)."""
    if language == TestLanguage.PYTHON and framework == TestFramework.PYTEST:
        code = PYTHON_PYTEST_TEMPLATES.get(library_id) or _default_pytest(library_id)
    elif language == TestLanguage.JAVASCRIPT and framework == TestFramework.JEST:
        code = JS_JEST_TEMPLATES.get(library_id) or _default_jest(library_id)
    elif language == TestLanguage.JAVASCRIPT and framework == TestFramework.MOCHA:
        code = JS_MOCHA_TEMPLATES.get(library_id) or _default_mocha(library_id)
    else:
        # Fallback: pytest for python, jest for JS
        if language == TestLanguage.PYTHON:
            code = _default_pytest(library_id)
        else:
            code = _default_jest(library_id)

    # Count test functions
    test_count = 0
    for line in code.split("\n"):
        stripped = line.strip()
        if stripped.startswith("def test_") or stripped.startswith("test(") or stripped.startswith("it("):
            test_count += 1

    return code, test_count


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateTestResponse)
async def generate_tests(request: GenerateTestRequest) -> GenerateTestResponse:
    """
    Generate integration test scaffolding for a library.

    Produces ready-to-run test files for popular Indian APIs (Razorpay, Zerodha)
    and generic test templates for other libraries.
    """
    if not flags.TEST_GENERATION:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    framework = _resolve_framework(request.language, request.framework)

    # Validate framework + language combination
    if request.language == TestLanguage.PYTHON and framework not in (TestFramework.PYTEST,):
        raise HTTPException(
            status_code=400,
            detail=f"Framework {framework.value} is not supported for Python. Use 'pytest'.",
        )
    if request.language == TestLanguage.JAVASCRIPT and framework not in (
        TestFramework.JEST,
        TestFramework.MOCHA,
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Framework {framework.value} is not supported for JavaScript. Use 'jest' or 'mocha'.",
        )

    try:
        code, test_count = _generate_tests(request.library_id, request.language, framework)

        known_libs = set(PYTHON_PYTEST_TEMPLATES.keys()) | set(JS_JEST_TEMPLATES.keys())
        is_known = request.library_id in known_libs

        explanation = (
            f"Generated {test_count} integration tests for {request.library_id} "
            f"using {framework.value}."
        )
        if is_known:
            explanation += " Tests include real SDK method calls for this library."
        else:
            explanation += " Tests use a generic template — replace TODO comments with actual API calls."

        return GenerateTestResponse(
            test_code=code.strip(),
            framework=framework.value,
            test_count=test_count,
            explanation=explanation,
        )
    except Exception as e:
        logger.error(
            "Test generation failed",
            extra={"library_id": request.library_id, "framework": framework.value},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Test generation failed: {e}")
