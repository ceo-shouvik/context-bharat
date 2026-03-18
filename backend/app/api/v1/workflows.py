"""Multi-API workflow templates — pre-built flows combining multiple Indian APIs."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.core.feature_flags import flags

router = APIRouter(prefix="/workflows", tags=["workflows"])

WORKFLOWS = {
    "ecommerce-india": {
        "id": "ecommerce-india",
        "title": "Indian E-Commerce Stack",
        "description": "Complete e-commerce flow: Razorpay payments + Shiprocket shipping + MSG91 notifications",
        "apis_involved": ["Razorpay", "Shiprocket", "MSG91"],
        "steps": [
            {"step": 1, "api": "MSG91", "action": "Send OTP for phone verification", "endpoint": "POST /api/v5/otp"},
            {"step": 2, "api": "Razorpay", "action": "Create payment order", "endpoint": "POST /v1/orders"},
            {"step": 3, "api": "Razorpay", "action": "Process payment (frontend checkout)", "endpoint": "Razorpay.js checkout"},
            {"step": 4, "api": "Razorpay", "action": "Verify payment signature", "endpoint": "Webhook: payment.captured"},
            {"step": 5, "api": "Shiprocket", "action": "Create shipping order", "endpoint": "POST /v1/external/orders/create/adhoc"},
            {"step": 6, "api": "Shiprocket", "action": "Generate AWB and schedule pickup", "endpoint": "POST /v1/external/courier/assign/awb"},
            {"step": 7, "api": "MSG91", "action": "Send order confirmation SMS", "endpoint": "POST /api/v5/flow"},
        ],
    },
    "fintech-kyc": {
        "id": "fintech-kyc",
        "title": "Fintech KYC + Onboarding",
        "description": "User verification: Aadhaar eKYC + DigiLocker + Razorpay account creation",
        "apis_involved": ["Aadhaar eKYC", "DigiLocker", "Razorpay"],
        "steps": [
            {"step": 1, "api": "Aadhaar eKYC", "action": "Send OTP to Aadhaar-linked mobile", "endpoint": "POST /otp"},
            {"step": 2, "api": "Aadhaar eKYC", "action": "Verify OTP and get KYC data", "endpoint": "POST /kyc"},
            {"step": 3, "api": "DigiLocker", "action": "Fetch PAN card from DigiLocker", "endpoint": "GET /api/1/file/{uri}"},
            {"step": 4, "api": "Razorpay", "action": "Create linked account (Route)", "endpoint": "POST /v2/accounts"},
            {"step": 5, "api": "Razorpay", "action": "Add bank account for settlements", "endpoint": "PATCH /v2/accounts/{id}"},
        ],
    },
    "saas-billing": {
        "id": "saas-billing",
        "title": "SaaS Billing + Invoicing",
        "description": "Subscription billing: Razorpay subscriptions + Zoho Books invoicing + MSG91 reminders",
        "apis_involved": ["Razorpay", "Zoho Books", "MSG91"],
        "steps": [
            {"step": 1, "api": "Razorpay", "action": "Create subscription plan", "endpoint": "POST /v1/plans"},
            {"step": 2, "api": "Razorpay", "action": "Create subscription for customer", "endpoint": "POST /v1/subscriptions"},
            {"step": 3, "api": "Razorpay", "action": "Handle subscription.charged webhook", "endpoint": "Webhook"},
            {"step": 4, "api": "Zoho Books", "action": "Create invoice in Zoho Books", "endpoint": "POST /api/v3/invoices"},
            {"step": 5, "api": "MSG91", "action": "Send payment receipt via SMS", "endpoint": "POST /api/v5/flow"},
        ],
    },
}

@router.get("")
async def list_workflows() -> dict:
    if not flags.WORKFLOW_TEMPLATES:
        raise HTTPException(status_code=404, detail="Feature not enabled")
    return {"workflows": [{"id": w["id"], "title": w["title"], "description": w["description"], "apis_involved": w["apis_involved"], "step_count": len(w["steps"])} for w in WORKFLOWS.values()], "total": len(WORKFLOWS)}

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> dict:
    if not flags.WORKFLOW_TEMPLATES:
        raise HTTPException(status_code=404, detail="Feature not enabled")
    wf = WORKFLOWS.get(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return wf
