"""DLT/Compliance layer — regulatory guidance for Indian API integrations."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compliance", tags=["compliance"])


# ── Pydantic Models ──────────────────────────────────────────────


class ComplianceRequirement(BaseModel):
    """A single regulatory or compliance requirement."""

    regulation: str = Field(..., description="Name of the regulation or standard")
    description: str = Field(..., description="What this regulation requires")
    severity: str = Field(
        ..., description="Impact level: critical, high, medium, low"
    )


class MandatoryField(BaseModel):
    """A field that must be included per regulatory requirements."""

    field_name: str
    description: str
    example: str


class ComplianceTip(BaseModel):
    """Practical implementation advice for compliance."""

    tip: str
    context: str


class ComplianceResponse(BaseModel):
    """Complete compliance information for a library."""

    library_id: str
    library_name: str
    requirements: list[ComplianceRequirement]
    mandatory_fields: list[MandatoryField]
    tips: list[ComplianceTip]
    last_reviewed: str = Field(
        ..., description="When this compliance data was last reviewed"
    )


# ── Compliance Data ──────────────────────────────────────────────

COMPLIANCE_DATA: dict[str, dict] = {
    "razorpay": {
        "library_name": "Razorpay",
        "requirements": [
            {
                "regulation": "PCI-DSS v4.0",
                "description": (
                    "All merchants handling card data must comply with PCI-DSS. "
                    "Razorpay is PCI-DSS Level 1 certified, but merchants using "
                    "Custom Checkout (where card fields render on merchant page) "
                    "must complete SAQ-A or SAQ-A-EP questionnaire. Standard "
                    "Checkout (hosted) shifts most PCI burden to Razorpay."
                ),
                "severity": "critical",
            },
            {
                "regulation": "RBI Data Localization (April 2018 Circular)",
                "description": (
                    "All payment system data must be stored only in India. "
                    "Razorpay handles this on their side, but if you store "
                    "transaction logs, card tokens, or payment metadata in your "
                    "own database, it must reside on servers physically located "
                    "in India. AWS ap-south-1 (Mumbai) or GCP asia-south1."
                ),
                "severity": "critical",
            },
            {
                "regulation": "RBI Recurring Payments Guidelines (Sept 2021)",
                "description": (
                    "e-mandates for recurring payments above INR 15,000 require "
                    "additional factor authentication (AFA) for each debit. "
                    "Razorpay Subscriptions API handles this, but you must send "
                    "pre-debit notifications 24 hours before charge. Use "
                    "razorpay.subscriptions.create() with proper notify_info."
                ),
                "severity": "high",
            },
            {
                "regulation": "RBI Tokenization (Oct 2022)",
                "description": (
                    "Merchants cannot store actual card numbers. Use Razorpay "
                    "Token HQ for network tokenization. card.token_iin and "
                    "card.last4 are the only card details you may persist."
                ),
                "severity": "critical",
            },
        ],
        "mandatory_fields": [
            {
                "field_name": "amount",
                "description": "Must be in paise (smallest currency unit). INR 500 = 50000 paise.",
                "example": "50000",
            },
            {
                "field_name": "currency",
                "description": "Three-letter ISO currency code. INR for Indian Rupee.",
                "example": "INR",
            },
            {
                "field_name": "receipt",
                "description": (
                    "Unique receipt ID from your system. Required for reconciliation "
                    "and RBI audit trail. Max 40 characters."
                ),
                "example": "receipt_order_20240315_001",
            },
        ],
        "tips": [
            {
                "tip": "Always verify webhook signatures using Razorpay.validateWebhookSignature()",
                "context": (
                    "Webhook signature validation prevents spoofed payment "
                    "confirmations. Use the webhook secret from Dashboard > "
                    "Settings > Webhooks, not your API key secret."
                ),
            },
            {
                "tip": "Use test mode keys (rzp_test_*) in staging, never live keys",
                "context": (
                    "Razorpay test mode simulates the full payment flow without "
                    "real transactions. Test card: 4111 1111 1111 1111, any future "
                    "expiry, any CVV. UPI test VPA: success@razorpay."
                ),
            },
            {
                "tip": "Implement idempotency keys for order creation",
                "context": (
                    "Network retries can cause duplicate orders. Pass a unique "
                    "receipt ID and check for existing orders before creating new "
                    "ones. Razorpay does not enforce idempotency automatically."
                ),
            },
        ],
        "last_reviewed": "2026-03-01",
    },
    "gstn": {
        "library_name": "GSTN (GST Network)",
        "requirements": [
            {
                "regulation": "GSTN API Access Rules",
                "description": (
                    "Direct GSTN API access requires GSP (GST Suvidha Provider) "
                    "partnership. Most developers should use a GSP like ClearTax, "
                    "MasterGST, or Cygnet. Direct API access requires GSTN "
                    "empanelment and security audit."
                ),
                "severity": "critical",
            },
            {
                "regulation": "e-Invoice Mandate (Phase 1-6)",
                "description": (
                    "Businesses with turnover above INR 5 crore must generate "
                    "e-invoices via IRP (Invoice Registration Portal). IRN "
                    "(Invoice Reference Number) must be generated within 30 days "
                    "of invoice date. Use /eivp/v1.03/Invoice API for generation."
                ),
                "severity": "critical",
            },
            {
                "regulation": "GSTIN Validation Rules",
                "description": (
                    "GSTIN is a 15-digit alphanumeric code. Format: "
                    "2 digits state code + 10 chars PAN + 1 entity code + 1 Z + "
                    "1 checksum. Always validate format before API call to avoid "
                    "rate limit penalties."
                ),
                "severity": "high",
            },
            {
                "regulation": "Data Retention — GST Act Section 35/36",
                "description": (
                    "GST records must be maintained for 6 years (72 months) from "
                    "the due date of filing annual return. Logs of API calls for "
                    "return filing and e-invoice generation must be preserved."
                ),
                "severity": "high",
            },
        ],
        "mandatory_fields": [
            {
                "field_name": "gstin",
                "description": "15-digit GSTIN of the taxpayer. Validate with regex: ^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
                "example": "27AAPFU0939F1ZV",
            },
            {
                "field_name": "ret_period",
                "description": "Return period in MMYYYY format.",
                "example": "032026",
            },
            {
                "field_name": "auth-token",
                "description": "OTP-based session token from /authenticate endpoint. Expires in 6 hours.",
                "example": "Bearer <session_token>",
            },
        ],
        "tips": [
            {
                "tip": "GSTN API rate limits are strict: 10 requests/minute per GSTIN",
                "context": (
                    "Exceeding rate limits results in 24-hour IP block. Implement "
                    "exponential backoff and queue GSTR filing requests. Batch "
                    "invoice uploads using /returnsapi/v1/returns/gstr1 with "
                    "multiple invoices per request."
                ),
            },
            {
                "tip": "Handle session expiry gracefully — GSTN sessions are OTP-based",
                "context": (
                    "GSTN auth requires OTP sent to registered mobile. Sessions "
                    "expire in 6 hours. Cache the auth-token and implement "
                    "automatic re-authentication. Never store OTPs."
                ),
            },
            {
                "tip": "Use sandbox mode for development: sandbox.gstn.org.in",
                "context": (
                    "GSTN sandbox provides test GSTINs and simulated returns. "
                    "Apply for sandbox access at developer.gstn.org.in. "
                    "Sandbox credentials are different from production."
                ),
            },
        ],
        "last_reviewed": "2026-02-15",
    },
    "msg91": {
        "library_name": "MSG91",
        "requirements": [
            {
                "regulation": "TRAI DLT Registration (Aug 2021)",
                "description": (
                    "All commercial SMS senders must register on a DLT "
                    "(Distributed Ledger Technology) platform (JioTruecaller, "
                    "Airtel Ads, Vodafone VILPOWER). Registration includes: "
                    "Entity registration, Header (sender ID) registration, and "
                    "Template registration. Without DLT registration, SMS will "
                    "be silently dropped by telecom operators."
                ),
                "severity": "critical",
            },
            {
                "regulation": "DLT Entity ID",
                "description": (
                    "Every business sending SMS must have a DLT Entity ID "
                    "(19-digit numeric). This must be configured in MSG91 "
                    "dashboard under Settings > DLT. MSG91 maps your entity ID "
                    "to the correct DLT platform automatically."
                ),
                "severity": "critical",
            },
            {
                "regulation": "Template Registration",
                "description": (
                    "Every SMS template must be pre-registered on DLT with exact "
                    "content and variable placeholders ({#var#}). Template types: "
                    "Transactional (OTP, alerts), Promotional (marketing), "
                    "Service Implicit/Explicit. Template approval takes 1-3 days."
                ),
                "severity": "critical",
            },
            {
                "regulation": "NDNC/DND Compliance",
                "description": (
                    "Promotional SMS cannot be sent to DND-registered numbers "
                    "(check via TRAI DND app). Transactional SMS (OTP, bank "
                    "alerts) are exempt. MSG91 handles DND filtering automatically "
                    "for promotional campaigns."
                ),
                "severity": "high",
            },
        ],
        "mandatory_fields": [
            {
                "field_name": "DLT_TE_ID",
                "description": "DLT template ID (19-digit) registered on your DLT platform.",
                "example": "1107161234567890123",
            },
            {
                "field_name": "sender",
                "description": "6-character alphanumeric sender ID registered on DLT.",
                "example": "MYBRND",
            },
            {
                "field_name": "route",
                "description": "SMS route: 1 (Promotional), 4 (Transactional), 106 (OTP-specific).",
                "example": "4",
            },
        ],
        "tips": [
            {
                "tip": "Register templates on DLT first, then configure in MSG91 — not the other way around",
                "context": (
                    "Common mistake: creating templates in MSG91 dashboard without "
                    "DLT approval. The SMS will fail silently. DLT template content "
                    "must exactly match what you send through MSG91, including "
                    "variable positions."
                ),
            },
            {
                "tip": "Use MSG91's SendOTP flow instead of building OTP logic from scratch",
                "context": (
                    "MSG91 SendOTP handles OTP generation, delivery, retry via "
                    "voice call, and verification in a single API. POST to "
                    "/api/v5/otp with mobile number. Verify with "
                    "/api/v5/otp/verify. Auto-retries on SMS failure."
                ),
            },
        ],
        "last_reviewed": "2026-02-20",
    },
    "npci/upi": {
        "library_name": "UPI / NPCI",
        "requirements": [
            {
                "regulation": "UPI 2.0 Specification Compliance",
                "description": (
                    "Third-party app providers (TPAPs) must integrate via a "
                    "sponsor PSP bank. Direct UPI API access is not available "
                    "to merchants — use a payment aggregator (Razorpay, Cashfree) "
                    "or become a TPAP registered with NPCI."
                ),
                "severity": "critical",
            },
            {
                "regulation": "UPI Transaction Limits (NPCI Circular 2024)",
                "description": (
                    "Per-transaction limit: INR 1,00,000 (general), "
                    "INR 5,00,000 (tax/education/IPO), INR 2,00,000 (capital "
                    "markets). Daily limit varies by bank. UPI Lite: INR 500 "
                    "per transaction, INR 2,000 wallet balance."
                ),
                "severity": "high",
            },
            {
                "regulation": "Mandate/Autopay Rules (UPI 2.0)",
                "description": (
                    "Recurring mandates must include: frequency (daily/weekly/"
                    "monthly/yearly), start and end date, maximum amount per "
                    "debit. First mandate requires PIN authentication. "
                    "Pre-debit notification mandatory 24 hours before execution."
                ),
                "severity": "high",
            },
            {
                "regulation": "RBI Two-Factor Authentication",
                "description": (
                    "UPI transactions inherently satisfy 2FA: device binding "
                    "(something you have) + UPI PIN (something you know). "
                    "Your integration must not bypass or cache UPI PINs."
                ),
                "severity": "critical",
            },
        ],
        "mandatory_fields": [
            {
                "field_name": "VPA (Virtual Payment Address)",
                "description": "Payer/payee UPI ID. Format: username@psp. Validate with regex: ^[a-zA-Z0-9.\\-_]{2,256}@[a-zA-Z]{2,64}$",
                "example": "merchant@ybl",
            },
            {
                "field_name": "txnId",
                "description": "Unique transaction ID. UUID v4 format. Must be unique per transaction.",
                "example": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            },
            {
                "field_name": "amount",
                "description": "Transaction amount in INR. Decimal up to 2 places. Minimum INR 1.00.",
                "example": "500.00",
            },
        ],
        "tips": [
            {
                "tip": "Handle collect request timeouts — UPI collect expires in 5 minutes by default",
                "context": (
                    "If the payer does not respond to a collect request within "
                    "the expiry window, the transaction status becomes EXPIRED. "
                    "Implement polling with /v1/transaction/status every 10 "
                    "seconds, and show a clear 'payment pending' state in your UI."
                ),
            },
            {
                "tip": "Always implement callback URL + polling for payment status",
                "context": (
                    "UPI payments are async. Never rely solely on callbacks — "
                    "network issues can cause missed webhooks. Implement both "
                    "callback handling AND periodic status polling. "
                    "Transaction status API is idempotent."
                ),
            },
            {
                "tip": "Test with NPCI UAT environment before going live",
                "context": (
                    "NPCI provides UAT (User Acceptance Testing) sandbox "
                    "through your PSP bank. Test all flows: pay, collect, "
                    "mandate create, mandate revoke, refund. UAT credentials "
                    "are issued by your sponsor bank, not NPCI directly."
                ),
            },
        ],
        "last_reviewed": "2026-02-28",
    },
    "ondc": {
        "library_name": "ONDC (Open Network for Digital Commerce)",
        "requirements": [
            {
                "regulation": "Beckn Protocol Compliance",
                "description": (
                    "All ONDC network participants must implement the Beckn "
                    "Protocol specification. This includes: /search, /select, "
                    "/init, /confirm, /status, /track, /cancel, /update, and "
                    "/rating APIs. Each API call must include a valid context "
                    "object with domain, action, bap_id, bpp_id, and "
                    "transaction_id."
                ),
                "severity": "critical",
            },
            {
                "regulation": "Ed25519 Request Signing",
                "description": (
                    "Every API request on the ONDC network must be signed using "
                    "Ed25519 (not RSA). The signing key pair must be registered "
                    "with the ONDC registry. Signature goes in the Authorization "
                    "header using the Beckn auth scheme. Invalid signatures "
                    "result in immediate request rejection."
                ),
                "severity": "critical",
            },
            {
                "regulation": "ONDC Registry Registration",
                "description": (
                    "Network participants must register on the ONDC registry "
                    "(registry.ondc.org). Registration includes: subscriber ID, "
                    "signing public key, encryption public key, callback URL, "
                    "supported domains (retail, logistics, financial services). "
                    "Registry lookup is required to verify counterparty."
                ),
                "severity": "critical",
            },
            {
                "regulation": "Schema Validation (ONDC v1.2.x)",
                "description": (
                    "All API payloads must conform to the ONDC JSON schema. "
                    "Use the ONDC log validation utility "
                    "(github.com/ONDC-Official/log-validation-utility) to "
                    "validate your implementation. Schema violations cause "
                    "network-level rejection."
                ),
                "severity": "high",
            },
        ],
        "mandatory_fields": [
            {
                "field_name": "context.bap_id",
                "description": "Buyer App subscriber ID registered with ONDC registry.",
                "example": "buyerapp.example.com",
            },
            {
                "field_name": "context.bpp_id",
                "description": "Seller App subscriber ID registered with ONDC registry.",
                "example": "sellerapp.example.com",
            },
            {
                "field_name": "context.transaction_id",
                "description": "UUID identifying the complete transaction lifecycle (search to confirm).",
                "example": "a9aaecca-10b7-4d19-b640-b047a7c60008",
            },
            {
                "field_name": "Authorization header",
                "description": "Beckn Authorization header with Ed25519 signature. Format: Signature keyId=\"<subscriber_id>|<key_id>|ed25519\",algorithm=\"ed25519\",created=\"<unix_ts>\",expires=\"<unix_ts>\",headers=\"(created) (expires) digest\",signature=\"<base64_sig>\"",
                "example": "Signature keyId=\"buyerapp.com|key1|ed25519\",algorithm=\"ed25519\",...",
            },
        ],
        "tips": [
            {
                "tip": "Use ONDC staging environment before production: staging.registry.ondc.org",
                "context": (
                    "ONDC provides a staging registry and gateway. All "
                    "development and testing should use staging. Production "
                    "access requires passing the ONDC certification process "
                    "(technical + business review)."
                ),
            },
            {
                "tip": "Implement async server-to-server callbacks properly",
                "context": (
                    "ONDC is fully async. When you call /search on the gateway, "
                    "the response comes via /on_search callback to your server. "
                    "Your server must be publicly accessible with a valid SSL "
                    "certificate. Use ngrok for local development."
                ),
            },
            {
                "tip": "Validate with ONDC log validation utility before certification",
                "context": (
                    "Run your API logs through "
                    "github.com/ONDC-Official/log-validation-utility. "
                    "This checks: schema compliance, context consistency, "
                    "timestamp ordering, and business logic rules. "
                    "Certification will use similar validation."
                ),
            },
        ],
        "last_reviewed": "2026-03-05",
    },
    "aadhaar": {
        "library_name": "Aadhaar eKYC / Authentication",
        "requirements": [
            {
                "regulation": "CCA (Certifying Authority) Partnership",
                "description": (
                    "Aadhaar authentication APIs are not publicly accessible. "
                    "You must partner with a licensed ASP (Authentication Service "
                    "Provider) who has a relationship with an ESP (E-KYC Service "
                    "Provider) licensed by UIDAI. Common ASPs: Khosla Labs, "
                    "Setu (formerly Signzy), Digio."
                ),
                "severity": "critical",
            },
            {
                "regulation": "ASP Certification",
                "description": (
                    "If building as an ASP, you need: STQC audit certification, "
                    "AUA (Authentication User Agency) license from UIDAI, "
                    "static IP whitelisting, HSM (Hardware Security Module) "
                    "for encrypting PID blocks. Annual audit required."
                ),
                "severity": "critical",
            },
            {
                "regulation": "Aadhaar Data Handling — DPDP Act 2023 + Aadhaar Act 2016",
                "description": (
                    "Aadhaar number must never be stored in plaintext. Only "
                    "the virtual ID (16-digit) or last 4 digits may be "
                    "displayed. Biometric data must not be stored at all. "
                    "Consent must be explicit and logged. Data must be "
                    "encrypted at rest (AES-256) and in transit (TLS 1.2+)."
                ),
                "severity": "critical",
            },
            {
                "regulation": "eKYC Response Data Retention",
                "description": (
                    "eKYC response data (name, address, photo) can only be "
                    "retained for the duration needed to complete the KYC "
                    "process. Long-term storage requires separate consent "
                    "and must comply with DPDP Act. Maximum retention: as "
                    "specified in your AUA license agreement."
                ),
                "severity": "high",
            },
        ],
        "mandatory_fields": [
            {
                "field_name": "uid/vid",
                "description": "12-digit Aadhaar number or 16-digit Virtual ID. Always prefer VID for privacy.",
                "example": "Virtual ID: 1234567890123456",
            },
            {
                "field_name": "PID block",
                "description": "Encrypted PID (Personal Identity Data) block containing OTP or biometric. Must be encrypted with UIDAI's public key using 2048-bit RSA + AES-256 session key.",
                "example": "(encrypted XML block)",
            },
            {
                "field_name": "AUA code",
                "description": "Your licensed AUA (Authentication User Agency) code issued by UIDAI.",
                "example": "AUA code from UIDAI license",
            },
        ],
        "tips": [
            {
                "tip": "Use Virtual ID (VID) instead of Aadhaar number wherever possible",
                "context": (
                    "VID is a revocable 16-digit number mapped to Aadhaar. "
                    "It provides the same authentication without exposing the "
                    "actual Aadhaar number. Users can generate VID from "
                    "resident.uidai.gov.in or mAadhaar app."
                ),
            },
            {
                "tip": "No public sandbox exists — use ASP partner's test environment",
                "context": (
                    "UIDAI does not provide a public sandbox. Your ASP partner "
                    "(Khosla Labs, Setu, Digio) will provide test credentials "
                    "and a staging environment. Test with their sandbox before "
                    "going through UIDAI certification."
                ),
            },
        ],
        "last_reviewed": "2026-02-10",
    },
}

# Map common library ID patterns to compliance data keys
_LIBRARY_ID_MAP: dict[str, str] = {
    "/razorpay/razorpay-sdk": "razorpay",
    "/razorpay": "razorpay",
    "razorpay": "razorpay",
    "/gstn/gst-api": "gstn",
    "/gstn": "gstn",
    "gstn": "gstn",
    "gst": "gstn",
    "/msg91/msg91-api": "msg91",
    "/msg91": "msg91",
    "msg91": "msg91",
    "/npci/upi-specs": "npci/upi",
    "/npci/upi": "npci/upi",
    "npci/upi": "npci/upi",
    "upi": "npci/upi",
    "/ondc/protocol-specs": "ondc",
    "/ondc": "ondc",
    "ondc": "ondc",
    "/uidai/aadhaar-ekyc": "aadhaar",
    "/aadhaar": "aadhaar",
    "aadhaar": "aadhaar",
}


# ── Endpoints ────────────────────────────────────────────────────


@router.get("/{library_id:path}", response_model=ComplianceResponse)
async def get_compliance(library_id: str) -> ComplianceResponse:
    """
    Get compliance notes and regulatory requirements for a library.

    Returns regulatory requirements, mandatory fields, and practical
    compliance tips specific to the library's domain. Covers PCI-DSS,
    RBI guidelines, DLT registration, GSTN rules, UPI specifications,
    Beckn protocol requirements, and Aadhaar data handling.

    Args:
        library_id: Canonical library ID or short name (e.g. "razorpay",
                    "/razorpay/razorpay-sdk", "gstn", "ondc").
    """
    if not flags.COMPLIANCE_LAYER:
        raise HTTPException(
            status_code=403,
            detail="Compliance layer is disabled. Set FEATURE_COMPLIANCE_LAYER=true to enable.",
        )

    # Resolve the library_id to a compliance data key
    normalized = library_id.strip().lower()
    data_key = _LIBRARY_ID_MAP.get(normalized) or _LIBRARY_ID_MAP.get(
        f"/{normalized}"
    )

    # Also try matching just the last path segment
    if data_key is None:
        last_segment = normalized.rstrip("/").rsplit("/", 1)[-1]
        data_key = _LIBRARY_ID_MAP.get(last_segment)

    if data_key is None or data_key not in COMPLIANCE_DATA:
        available = sorted({v for v in _LIBRARY_ID_MAP.values()})
        raise HTTPException(
            status_code=404,
            detail=(
                f"No compliance data found for '{library_id}'. "
                f"Available: {', '.join(available)}"
            ),
        )

    data = COMPLIANCE_DATA[data_key]
    logger.info(
        "Serving compliance data",
        extra={"library_id": library_id, "resolved_key": data_key},
    )

    return ComplianceResponse(
        library_id=library_id,
        library_name=data["library_name"],
        requirements=[ComplianceRequirement(**r) for r in data["requirements"]],
        mandatory_fields=[MandatoryField(**f) for f in data["mandatory_fields"]],
        tips=[ComplianceTip(**t) for t in data["tips"]],
        last_reviewed=data["last_reviewed"],
    )
