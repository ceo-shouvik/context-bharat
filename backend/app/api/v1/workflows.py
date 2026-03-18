"""Multi-API workflow templates — pre-built flows combining multiple Indian APIs."""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ─── Schemas ─────────────────────────────────────────────────────────────────


class DiagramStep(BaseModel):
    step: int
    api: str
    action: str
    endpoint: str
    description: str = ""


class WorkflowSummary(BaseModel):
    id: str
    title: str
    description: str
    apis_involved: list[str]
    step_count: int


class WorkflowDetail(BaseModel):
    id: str
    title: str
    description: str
    apis_involved: list[str]
    prerequisites: list[str]
    steps: list[DiagramStep]
    code_per_step: dict[str, str]
    architecture_notes: str


class WorkflowListResponse(BaseModel):
    workflows: list[WorkflowSummary]
    total: int


# ─── Data ────────────────────────────────────────────────────────────────────

WORKFLOWS: dict[str, dict[str, Any]] = {
    "ecommerce-india": {
        "id": "ecommerce-india",
        "title": "Indian E-Commerce Stack",
        "description": (
            "Complete e-commerce flow: OTP-verified checkout via MSG91, "
            "Razorpay payment processing with webhook verification, "
            "Shiprocket shipping with auto-courier selection, and SMS order confirmation."
        ),
        "apis_involved": ["/razorpay/razorpay-sdk", "/shiprocket/shiprocket-api", "/msg91/msg91-api"],
        "prerequisites": [
            "Razorpay account (test mode)",
            "Shiprocket account with pickup location",
            "MSG91 account with OTP + transactional templates",
        ],
        "steps": [
            {"step": 1, "api": "MSG91", "action": "Send OTP for phone verification",
             "endpoint": "POST /api/v5/otp",
             "description": "Verify customer's mobile before checkout to reduce fraud."},
            {"step": 2, "api": "MSG91", "action": "Verify OTP",
             "endpoint": "GET /api/v5/otp/verify",
             "description": "Validate OTP. Only proceed to payment if valid."},
            {"step": 3, "api": "Razorpay", "action": "Create payment order",
             "endpoint": "POST /v1/orders",
             "description": "Create Razorpay order with cart amount. Return order_id to frontend."},
            {"step": 4, "api": "Razorpay", "action": "Process payment via checkout",
             "endpoint": "Razorpay.js checkout",
             "description": "Frontend opens Razorpay checkout. On success, webhook fires."},
            {"step": 5, "api": "Razorpay", "action": "Verify payment webhook",
             "endpoint": "Webhook: payment.captured",
             "description": "Verify HMAC signature on webhook. Confirm payment."},
            {"step": 6, "api": "Shiprocket", "action": "Create shipping order",
             "endpoint": "POST /v1/external/orders/create/adhoc",
             "description": "Create Shiprocket order with address and items after payment confirmation."},
            {"step": 7, "api": "Shiprocket", "action": "Assign courier and get AWB",
             "endpoint": "POST /v1/external/courier/assign/awb",
             "description": "Auto-select best courier by cost and serviceability."},
            {"step": 8, "api": "MSG91", "action": "Send order confirmation SMS",
             "endpoint": "POST /api/v5/flow",
             "description": "SMS with order ID, tracking link, and estimated delivery."},
        ],
        "code_per_step": {
            "step_1_send_otp": '''import requests

MSG91_AUTH = "your_auth_key"
MSG91_TPL = "your_template_id"

def send_otp(mobile: str) -> bool:
    resp = requests.post("https://control.msg91.com/api/v5/otp", json={
        "template_id": MSG91_TPL, "mobile": f"91{mobile}", "otp_length": 6, "otp_expiry": 5,
    }, headers={"authkey": MSG91_AUTH})
    return resp.json().get("type") == "success"
''',
            "step_2_verify_otp": '''def verify_otp(mobile: str, otp: str) -> bool:
    resp = requests.get("https://control.msg91.com/api/v5/otp/verify",
        params={"mobile": f"91{mobile}", "otp": otp},
        headers={"authkey": MSG91_AUTH})
    return resp.json().get("type") == "success"
''',
            "step_3_create_order": '''import razorpay

rzp = razorpay.Client(auth=("rzp_test_XXXX", "secret_XXXX"))

def create_payment_order(amount_inr: int, mobile: str) -> dict:
    order = rzp.order.create({
        "amount": amount_inr * 100, "currency": "INR",
        "receipt": f"order_{mobile}", "notes": {"mobile": mobile},
    })
    return {"order_id": order["id"], "amount": order["amount"]}
''',
            "step_5_verify_webhook": '''import hmac, hashlib

def verify_razorpay_webhook(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
''',
            "step_6_create_shipment": '''SR_TOKEN = "shiprocket_token"
SR_BASE = "https://apiv2.shiprocket.in/v1/external"

def create_shipment(payment: dict, items: list, address: dict) -> dict:
    headers = {"Authorization": f"Bearer {SR_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(f"{SR_BASE}/orders/create/adhoc", json={
        "order_id": payment["order_id"],
        "order_date": "2024-03-15",
        "pickup_location": "Primary",
        "billing_customer_name": address["name"],
        "billing_address": address["address"],
        "billing_city": address["city"],
        "billing_pincode": address["pincode"],
        "billing_state": address["state"],
        "billing_country": "India",
        "billing_phone": payment.get("contact", ""),
        "shipping_is_billing": True,
        "order_items": items,
        "payment_method": "Prepaid",
        "sub_total": payment["amount"] / 100,
        "length": 20, "breadth": 15, "height": 10, "weight": 0.5,
    }, headers=headers)
    return resp.json()
''',
            "step_7_assign_courier": '''def assign_courier(shipment_id: int) -> dict:
    headers = {"Authorization": f"Bearer {SR_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(f"{SR_BASE}/courier/assign/awb",
        json={"shipment_id": shipment_id}, headers=headers)
    return resp.json()
''',
            "step_8_send_confirmation": '''def send_order_sms(mobile: str, order_id: str, awb: str, eta: str):
    requests.post("https://control.msg91.com/api/v5/flow", json={
        "template_id": "confirmation_template",
        "recipients": [{"mobiles": f"91{mobile}", "order_id": order_id, "awb": awb, "eta": eta}],
    }, headers={"authkey": MSG91_AUTH})
''',
        },
        "architecture_notes": (
            "Event-driven: Razorpay webhook triggers shipment creation asynchronously. "
            "Use Celery/Redis for reliable webhook-to-shipment processing. "
            "Store order state in DB and update at each step for auditability."
        ),
    },
    "fintech-kyc": {
        "id": "fintech-kyc",
        "title": "Fintech KYC + Onboarding",
        "description": (
            "User verification flow: Aadhaar eKYC via licensed ASP, PAN fetch from DigiLocker, "
            "name matching, and Razorpay linked account creation after KYC approval."
        ),
        "apis_involved": ["/uidai/aadhaar-ekyc", "/nsdl/digilocker-api", "/razorpay/razorpay-sdk"],
        "prerequisites": [
            "Aadhaar eKYC via licensed ASP (Setu, Signzy, Digio)",
            "DigiLocker Issuer/Requester registration",
            "Razorpay Route (marketplace) account",
            "DPDP Act compliance for data handling",
        ],
        "steps": [
            {"step": 1, "api": "Internal", "action": "Collect DPDP-compliant consent",
             "endpoint": "Internal",
             "description": "Record consent with timestamp, purpose, and data categories."},
            {"step": 2, "api": "Aadhaar eKYC (via ASP)", "action": "Send OTP to Aadhaar-linked mobile",
             "endpoint": "POST /okyc/otp/initiate",
             "description": "OTP sent to mobile linked to Aadhaar. Requires ASP partnership."},
            {"step": 3, "api": "Aadhaar eKYC (via ASP)", "action": "Verify OTP and get KYC data",
             "endpoint": "POST /okyc/otp/verify",
             "description": "Returns name, DOB, gender, address from Aadhaar."},
            {"step": 4, "api": "DigiLocker", "action": "Fetch PAN from DigiLocker",
             "endpoint": "GET /public/oauth2/3/files/issued",
             "description": "Fetch verified PAN card document. Match name with Aadhaar data."},
            {"step": 5, "api": "Internal", "action": "Name matching and risk scoring",
             "endpoint": "Internal",
             "description": "Fuzzy match Aadhaar name with PAN name. Flag mismatches for review."},
            {"step": 6, "api": "Razorpay", "action": "Create linked account (Route)",
             "endpoint": "POST /v2/accounts",
             "description": "Create Razorpay linked account for verified user to receive payouts."},
        ],
        "code_per_step": {
            "step_1_consent": '''from datetime import datetime, timezone

def record_consent(user_id: str, purpose: str) -> dict:
    return {
        "user_id": user_id, "purpose": purpose,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_categories": ["identity", "address", "financial"],
        "retention_period_days": 365,
    }
''',
            "step_2_aadhaar_otp": '''# Via Setu (licensed ASP)
import requests

SETU_BASE = "https://dg-sandbox.setu.co"

def initiate_aadhaar_otp(aadhaar_number: str) -> dict:
    resp = requests.post(f"{SETU_BASE}/api/digilocker/okyc/otp/initiate",
        json={"aadhaarNumber": aadhaar_number},
        headers={"x-client-id": "CLIENT_ID", "x-client-secret": "SECRET"})
    return resp.json()
''',
            "step_3_verify_kyc": '''def verify_aadhaar_otp(request_id: str, otp: str) -> dict:
    resp = requests.post(f"{SETU_BASE}/api/digilocker/okyc/otp/verify",
        json={"requestId": request_id, "otp": otp},
        headers={"x-client-id": "CLIENT_ID", "x-client-secret": "SECRET"})
    return resp.json()  # name, dob, gender, address
''',
            "step_5_name_match": '''from difflib import SequenceMatcher

def match_names(aadhaar_name: str, pan_name: str) -> dict:
    ratio = SequenceMatcher(None, aadhaar_name.lower(), pan_name.lower()).ratio()
    return {
        "match_score": round(ratio, 3),
        "status": "matched" if ratio > 0.85 else "review" if ratio > 0.6 else "mismatched",
    }
''',
            "step_6_razorpay_account": '''import razorpay
rzp = razorpay.Client(auth=("rzp_test_XXXX", "secret_XXXX"))

def create_linked_account(kyc: dict) -> dict:
    account = rzp.account.create({
        "email": kyc["email"], "phone": kyc["phone"],
        "legal_business_name": kyc["name"],
        "business_type": "individual",
        "legal_info": {"pan": kyc["pan_number"]},
    })
    return {"account_id": account["id"], "status": account["status"]}
''',
        },
        "architecture_notes": (
            "KYC data is PII under DPDP Act. Encrypt at rest, use field-level encryption "
            "for Aadhaar numbers. Consent required before data collection. "
            "Aadhaar eKYC needs a licensed ASP — no direct UIDAI access."
        ),
    },
    "saas-billing": {
        "id": "saas-billing",
        "title": "SaaS Billing + Invoicing",
        "description": (
            "Subscription billing: Razorpay recurring payments, "
            "Zoho Books GST-compliant invoice auto-generation, "
            "and MSG91 notifications for payment events."
        ),
        "apis_involved": ["/razorpay/razorpay-sdk", "/zoho/zoho-books-api", "/msg91/msg91-api"],
        "prerequisites": [
            "Razorpay with Subscriptions enabled",
            "Zoho Books account with API access",
            "MSG91 account with approved templates",
            "GSTIN for GST-compliant invoicing",
        ],
        "steps": [
            {"step": 1, "api": "Razorpay", "action": "Create subscription plan",
             "endpoint": "POST /v1/plans",
             "description": "Define monthly/annual plans with INR pricing."},
            {"step": 2, "api": "Razorpay", "action": "Create subscription for customer",
             "endpoint": "POST /v1/subscriptions",
             "description": "Create subscription. Razorpay handles recurring billing."},
            {"step": 3, "api": "Razorpay", "action": "Handle subscription.charged webhook",
             "endpoint": "Webhook: subscription.charged",
             "description": "On each successful payment, trigger invoice generation."},
            {"step": 4, "api": "Zoho Books", "action": "Create GST invoice",
             "endpoint": "POST /api/v3/invoices",
             "description": "Auto-create invoice with HSN/SAC codes, GST calculation."},
            {"step": 5, "api": "MSG91", "action": "Send receipt SMS",
             "endpoint": "POST /api/v5/flow",
             "description": "Email and SMS the invoice link to customer."},
        ],
        "code_per_step": {
            "step_1_create_plan": '''import razorpay
rzp = razorpay.Client(auth=("rzp_test_XXXX", "secret_XXXX"))

def create_plan(name: str, amount_inr: int, period: str = "monthly") -> dict:
    plan = rzp.plan.create({
        "period": period, "interval": 1,
        "item": {"name": name, "amount": amount_inr * 100, "currency": "INR"},
    })
    return {"plan_id": plan["id"]}
''',
            "step_2_create_subscription": '''def create_subscription(plan_id: str, email: str, mobile: str) -> dict:
    sub = rzp.subscription.create({
        "plan_id": plan_id, "total_count": 12, "quantity": 1,
        "notify_info": {"notify_phone": mobile, "notify_email": email},
    })
    return {"subscription_id": sub["id"], "short_url": sub["short_url"]}
''',
            "step_4_zoho_invoice": '''import requests

ZOHO_TOKEN = "zoho_oauth_token"
ZOHO_ORG = "org_id"

def create_gst_invoice(customer_id: str, amount: float, plan: str, payment_id: str) -> dict:
    resp = requests.post(
        f"https://www.zohoapis.in/books/v3/invoices",
        json={"JSONString": {
            "customer_id": customer_id,
            "is_inclusive_tax": False,
            "gst_treatment": "business_gst",
            "line_items": [{
                "name": plan, "rate": amount, "quantity": 1,
                "tax_id": "18_percent_gst", "hsn_or_sac": "998314",
            }],
            "notes": f"Razorpay: {payment_id}",
        }},
        headers={"Authorization": f"Zoho-oauthtoken {ZOHO_TOKEN}"},
        params={"organization_id": ZOHO_ORG},
    )
    return resp.json()["invoice"]
''',
            "step_5_notify": '''def send_receipt(mobile: str, invoice_url: str, amount: float):
    requests.post("https://control.msg91.com/api/v5/flow", json={
        "template_id": "invoice_tpl",
        "recipients": [{"mobiles": f"91{mobile}", "url": invoice_url, "amount": str(amount)}],
    }, headers={"authkey": "msg91_key"})
''',
        },
        "architecture_notes": (
            "For GST compliance, every subscription payment must generate an invoice. "
            "Zoho Books handles HSN/SAC codes and GSTR-1 filing data. "
            "Use Razorpay webhooks as source of truth for billing events."
        ),
    },
}


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.get("", response_model=WorkflowListResponse)
async def list_workflows() -> WorkflowListResponse:
    """List all available multi-API workflow templates."""
    if not flags.WORKFLOW_TEMPLATES:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    summaries = [
        WorkflowSummary(
            id=wf["id"],
            title=wf["title"],
            description=wf["description"],
            apis_involved=wf["apis_involved"],
            step_count=len(wf["steps"]),
        )
        for wf in WORKFLOWS.values()
    ]
    return WorkflowListResponse(workflows=summaries, total=len(summaries))


@router.get("/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow(workflow_id: str) -> WorkflowDetail:
    """Get a workflow with architecture diagram, step-by-step code, and notes."""
    if not flags.WORKFLOW_TEMPLATES:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    wf = WORKFLOWS.get(workflow_id)
    if not wf:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{workflow_id}' not found. Use GET /v1/workflows to list available workflows.",
        )

    steps = [DiagramStep(**s) for s in wf["steps"]]
    return WorkflowDetail(
        id=wf["id"],
        title=wf["title"],
        description=wf["description"],
        apis_involved=wf["apis_involved"],
        prerequisites=wf.get("prerequisites", []),
        steps=steps,
        code_per_step=wf.get("code_per_step", {}),
        architecture_notes=wf.get("architecture_notes", ""),
    )
