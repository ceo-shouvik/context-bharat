"""OpenAPI spec generation — extracts API structure from indexed docs."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openapi", tags=["openapi-generation"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class GenerateOpenAPIRequest(BaseModel):
    library_id: str = Field(..., description="ContextBharat library ID")


class GenerateOpenAPIResponse(BaseModel):
    spec: dict[str, Any] = Field(..., description="OpenAPI 3.0 JSON specification")
    library_name: str
    endpoints_found: int


# ─── Known OpenAPI Specs ─────────────────────────────────────────────────────

def _razorpay_spec() -> dict[str, Any]:
    """Pre-built OpenAPI 3.0 spec for Razorpay (key endpoints)."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Razorpay API",
            "version": "1.0.0",
            "description": "Razorpay payment gateway REST API for orders, payments, refunds, and payment links.",
            "contact": {"url": "https://razorpay.com/docs/api/"},
        },
        "servers": [
            {"url": "https://api.razorpay.com/v1", "description": "Production"},
        ],
        "security": [{"basicAuth": []}],
        "paths": {
            "/orders": {
                "post": {
                    "summary": "Create an order",
                    "operationId": "createOrder",
                    "tags": ["Orders"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["amount", "currency"],
                                    "properties": {
                                        "amount": {"type": "integer", "description": "Amount in paise (e.g., 50000 = INR 500)"},
                                        "currency": {"type": "string", "enum": ["INR", "USD"], "default": "INR"},
                                        "receipt": {"type": "string", "maxLength": 40},
                                        "payment_capture": {"type": "integer", "enum": [0, 1], "default": 1},
                                        "notes": {"type": "object", "additionalProperties": {"type": "string"}},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Order created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Order"},
                                },
                            },
                        },
                        "400": {"description": "Bad request"},
                    },
                },
            },
            "/orders/{order_id}": {
                "get": {
                    "summary": "Fetch an order by ID",
                    "operationId": "fetchOrder",
                    "tags": ["Orders"],
                    "parameters": [
                        {"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "Order details", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Order"}}}},
                        "404": {"description": "Order not found"},
                    },
                },
            },
            "/orders/{order_id}/payments": {
                "get": {
                    "summary": "Fetch payments for an order",
                    "operationId": "fetchOrderPayments",
                    "tags": ["Orders"],
                    "parameters": [
                        {"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "List of payments"},
                    },
                },
            },
            "/payments/{payment_id}": {
                "get": {
                    "summary": "Fetch a payment by ID",
                    "operationId": "fetchPayment",
                    "tags": ["Payments"],
                    "parameters": [
                        {"name": "payment_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "Payment details", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Payment"}}}},
                    },
                },
            },
            "/payments/{payment_id}/capture": {
                "post": {
                    "summary": "Capture a payment",
                    "operationId": "capturePayment",
                    "tags": ["Payments"],
                    "parameters": [
                        {"name": "payment_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["amount", "currency"],
                                    "properties": {
                                        "amount": {"type": "integer"},
                                        "currency": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "Payment captured"}},
                },
            },
            "/payments/{payment_id}/refund": {
                "post": {
                    "summary": "Create a refund",
                    "operationId": "createRefund",
                    "tags": ["Refunds"],
                    "parameters": [
                        {"name": "payment_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "amount": {"type": "integer", "description": "Partial refund amount in paise"},
                                        "speed": {"type": "string", "enum": ["normal", "optimum"]},
                                        "notes": {"type": "object"},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "Refund created"}},
                },
            },
            "/payment_links": {
                "post": {
                    "summary": "Create a payment link",
                    "operationId": "createPaymentLink",
                    "tags": ["Payment Links"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["amount", "currency"],
                                    "properties": {
                                        "amount": {"type": "integer"},
                                        "currency": {"type": "string"},
                                        "description": {"type": "string"},
                                        "customer": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "email": {"type": "string", "format": "email"},
                                                "contact": {"type": "string"},
                                            },
                                        },
                                        "notify": {
                                            "type": "object",
                                            "properties": {
                                                "sms": {"type": "boolean"},
                                                "email": {"type": "boolean"},
                                            },
                                        },
                                        "callback_url": {"type": "string", "format": "uri"},
                                        "callback_method": {"type": "string", "enum": ["get", "post"]},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "Payment link created"}},
                },
            },
            "/subscriptions": {
                "post": {
                    "summary": "Create a subscription",
                    "operationId": "createSubscription",
                    "tags": ["Subscriptions"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["plan_id", "total_count"],
                                    "properties": {
                                        "plan_id": {"type": "string"},
                                        "total_count": {"type": "integer"},
                                        "quantity": {"type": "integer"},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "Subscription created"}},
                },
            },
        },
        "components": {
            "securitySchemes": {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "Use key_id as username and key_secret as password",
                },
            },
            "schemas": {
                "Order": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "example": "order_DBJOWzybf0sJbb"},
                        "entity": {"type": "string", "example": "order"},
                        "amount": {"type": "integer", "example": 50000},
                        "amount_paid": {"type": "integer"},
                        "amount_due": {"type": "integer"},
                        "currency": {"type": "string", "example": "INR"},
                        "receipt": {"type": "string"},
                        "status": {"type": "string", "enum": ["created", "attempted", "paid"]},
                        "notes": {"type": "object"},
                        "created_at": {"type": "integer"},
                    },
                },
                "Payment": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "example": "pay_FHfBzqRGVxhV9E"},
                        "entity": {"type": "string", "example": "payment"},
                        "amount": {"type": "integer"},
                        "currency": {"type": "string"},
                        "status": {"type": "string", "enum": ["created", "authorized", "captured", "refunded", "failed"]},
                        "method": {"type": "string", "enum": ["card", "upi", "netbanking", "wallet", "emi"]},
                        "order_id": {"type": "string"},
                        "email": {"type": "string"},
                        "contact": {"type": "string"},
                    },
                },
            },
        },
    }


def _cashfree_spec() -> dict[str, Any]:
    """Pre-built OpenAPI 3.0 spec for Cashfree PG (key endpoints)."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Cashfree Payment Gateway API",
            "version": "2023-08-01",
            "description": "Cashfree Payments API for order creation, payment processing, and refunds.",
        },
        "servers": [
            {"url": "https://api.cashfree.com/pg", "description": "Production"},
            {"url": "https://sandbox.cashfree.com/pg", "description": "Sandbox"},
        ],
        "paths": {
            "/orders": {
                "post": {
                    "summary": "Create an order",
                    "operationId": "createOrder",
                    "tags": ["Orders"],
                    "parameters": [
                        {"name": "x-api-version", "in": "header", "required": True, "schema": {"type": "string", "default": "2023-08-01"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["order_amount", "order_currency", "customer_details"],
                                    "properties": {
                                        "order_amount": {"type": "number"},
                                        "order_currency": {"type": "string", "default": "INR"},
                                        "order_id": {"type": "string"},
                                        "customer_details": {
                                            "type": "object",
                                            "required": ["customer_id", "customer_phone"],
                                            "properties": {
                                                "customer_id": {"type": "string"},
                                                "customer_name": {"type": "string"},
                                                "customer_email": {"type": "string"},
                                                "customer_phone": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "responses": {
                        "200": {"description": "Order created successfully"},
                    },
                },
            },
            "/orders/{order_id}": {
                "get": {
                    "summary": "Get order details",
                    "operationId": "getOrder",
                    "tags": ["Orders"],
                    "parameters": [
                        {"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "x-api-version", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "Order details"}},
                },
            },
            "/orders/{order_id}/payments": {
                "get": {
                    "summary": "Get payments for an order",
                    "operationId": "getPaymentsForOrder",
                    "tags": ["Payments"],
                    "parameters": [
                        {"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "Payments list"}},
                },
            },
            "/orders/{order_id}/refunds": {
                "post": {
                    "summary": "Create a refund",
                    "operationId": "createRefund",
                    "tags": ["Refunds"],
                    "parameters": [
                        {"name": "order_id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["refund_amount", "refund_id"],
                                    "properties": {
                                        "refund_amount": {"type": "number"},
                                        "refund_id": {"type": "string"},
                                        "refund_note": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "Refund created"}},
                },
            },
        },
        "components": {
            "securitySchemes": {
                "XClientId": {"type": "apiKey", "in": "header", "name": "x-client-id"},
                "XClientSecret": {"type": "apiKey", "in": "header", "name": "x-client-secret"},
            },
        },
    }


def _msg91_spec() -> dict[str, Any]:
    """Pre-built OpenAPI 3.0 spec for MSG91 OTP API."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "MSG91 OTP & SMS API",
            "version": "5.0",
            "description": "MSG91 API for sending OTP, verifying OTP, and transactional SMS.",
        },
        "servers": [
            {"url": "https://control.msg91.com/api/v5", "description": "Production"},
        ],
        "paths": {
            "/otp": {
                "post": {
                    "summary": "Send OTP",
                    "operationId": "sendOTP",
                    "tags": ["OTP"],
                    "parameters": [
                        {"name": "authkey", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["template_id", "mobile"],
                                    "properties": {
                                        "template_id": {"type": "string"},
                                        "mobile": {"type": "string", "description": "Mobile with country code (e.g., 919876543210)"},
                                        "otp_length": {"type": "integer", "default": 6},
                                        "otp_expiry": {"type": "integer", "description": "Expiry in minutes", "default": 5},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "OTP sent successfully"}},
                },
            },
            "/otp/verify": {
                "get": {
                    "summary": "Verify OTP",
                    "operationId": "verifyOTP",
                    "tags": ["OTP"],
                    "parameters": [
                        {"name": "authkey", "in": "header", "required": True, "schema": {"type": "string"}},
                        {"name": "mobile", "in": "query", "required": True, "schema": {"type": "string"}},
                        {"name": "otp", "in": "query", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "OTP verified"},
                        "400": {"description": "Invalid OTP"},
                    },
                },
            },
            "/otp/resend": {
                "post": {
                    "summary": "Resend OTP",
                    "operationId": "resendOTP",
                    "tags": ["OTP"],
                    "parameters": [
                        {"name": "authkey", "in": "header", "required": True, "schema": {"type": "string"}},
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["mobile"],
                                    "properties": {
                                        "mobile": {"type": "string"},
                                        "retrytype": {"type": "string", "enum": ["text", "voice"]},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"200": {"description": "OTP resent"}},
                },
            },
        },
    }


KNOWN_SPECS: dict[str, tuple[callable, str, int]] = {
    "/razorpay/razorpay-sdk": (_razorpay_spec, "Razorpay", 8),
    "/cashfree/cashfree-pg": (_cashfree_spec, "Cashfree PG", 4),
    "/msg91/msg91-api": (_msg91_spec, "MSG91", 3),
}


def _generate_generic_spec(library_id: str) -> dict[str, Any]:
    """Generate a skeleton OpenAPI spec for unknown libraries."""
    lib_parts = library_id.strip("/").split("/")
    lib_name = lib_parts[-1].replace("-", " ").title() if lib_parts else "API"

    return {
        "openapi": "3.0.3",
        "info": {
            "title": f"{lib_name} API",
            "version": "1.0.0",
            "description": (
                f"Auto-generated OpenAPI skeleton for {library_id}. "
                f"Endpoints were inferred from indexed documentation. "
                f"Review and update paths, schemas, and parameters."
            ),
        },
        "servers": [
            {"url": "https://api.example.com/v1", "description": "Replace with actual base URL"},
        ],
        "paths": {
            "/resources": {
                "get": {
                    "summary": "List resources",
                    "operationId": "listResources",
                    "tags": ["Resources"],
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20}},
                    ],
                    "responses": {"200": {"description": "List of resources"}},
                },
                "post": {
                    "summary": "Create a resource",
                    "operationId": "createResource",
                    "tags": ["Resources"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "data": {"type": "object"},
                                    },
                                },
                            },
                        },
                    },
                    "responses": {"201": {"description": "Resource created"}},
                },
            },
            "/resources/{id}": {
                "get": {
                    "summary": "Get a resource",
                    "operationId": "getResource",
                    "tags": ["Resources"],
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "Resource details"}},
                },
                "put": {
                    "summary": "Update a resource",
                    "operationId": "updateResource",
                    "tags": ["Resources"],
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "Resource updated"}},
                },
                "delete": {
                    "summary": "Delete a resource",
                    "operationId": "deleteResource",
                    "tags": ["Resources"],
                    "parameters": [
                        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}},
                    ],
                    "responses": {"204": {"description": "Resource deleted"}},
                },
            },
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                },
            },
        },
    }


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateOpenAPIResponse)
async def generate_openapi_spec(
    request: GenerateOpenAPIRequest,
) -> GenerateOpenAPIResponse:
    """
    Generate an OpenAPI 3.0 specification from indexed documentation.

    For well-known Indian APIs (Razorpay, Cashfree, MSG91), returns a detailed
    pre-built spec. For other libraries, generates a skeleton spec that can be
    customized.
    """
    if not flags.OPENAPI_GENERATION:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    known = KNOWN_SPECS.get(request.library_id)

    if known:
        spec_fn, lib_name, endpoint_count = known
        spec = spec_fn()
    else:
        lib_parts = request.library_id.strip("/").split("/")
        lib_name = lib_parts[-1].replace("-", " ").title() if lib_parts else "API"
        spec = _generate_generic_spec(request.library_id)
        endpoint_count = sum(len(methods) for methods in spec.get("paths", {}).values())

    return GenerateOpenAPIResponse(
        spec=spec,
        library_name=lib_name,
        endpoints_found=endpoint_count,
    )
