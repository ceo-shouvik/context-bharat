"""Framework starter templates — pre-built projects combining Indian APIs with popular frameworks."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/starters", tags=["starters"])


# ─── Schemas ─────────────────────────────────────────────────────────────────


class StarterSummary(BaseModel):
    id: str
    title: str
    framework: str
    apis: list[str]
    description: str
    file_count: int


class StarterDetail(BaseModel):
    id: str
    title: str
    framework: str
    apis: list[str]
    description: str
    setup_instructions: list[str]
    files: dict[str, str]


class StarterListResponse(BaseModel):
    starters: list[StarterSummary]
    total: int


# ─── Data ────────────────────────────────────────────────────────────────────

STARTERS = {
    "nextjs-razorpay": {
        "id": "nextjs-razorpay",
        "title": "Next.js + Razorpay Payments",
        "framework": "Next.js 15",
        "apis": ["/razorpay/razorpay-sdk"],
        "description": (
            "Full-stack payment integration with App Router, server-side order creation, "
            "client-side Razorpay checkout, and webhook signature verification."
        ),
        "setup_instructions": [
            "npx create-next-app@latest my-app --typescript --tailwind --app",
            "cd my-app && npm install razorpay",
            "Copy files below into your project",
            "Add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to .env.local",
            "npm run dev",
        ],
        "files": {
            ".env.local": (
                "RAZORPAY_KEY_ID=rzp_test_XXXX\n"
                "RAZORPAY_KEY_SECRET=secret_XXXX\n"
                "NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_XXXX\n"
            ),
            "app/api/orders/route.ts": '''import Razorpay from "razorpay";
import { NextRequest, NextResponse } from "next/server";

const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID!,
  key_secret: process.env.RAZORPAY_KEY_SECRET!,
});

export async function POST(request: NextRequest) {
  try {
    const { amount, currency = "INR" } = await request.json();
    const order = await razorpay.orders.create({
      amount: amount * 100,
      currency,
      receipt: `order_${Date.now()}`,
    });
    return NextResponse.json({
      orderId: order.id,
      amount: order.amount,
      currency: order.currency,
    });
  } catch (error) {
    console.error("Order creation failed:", error);
    return NextResponse.json({ error: "Failed to create order" }, { status: 500 });
  }
}
''',
            "app/api/webhooks/razorpay/route.ts": '''import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get("x-razorpay-signature") || "";
  const secret = process.env.RAZORPAY_WEBHOOK_SECRET || "";

  const expected = crypto.createHmac("sha256", secret).update(body).digest("hex");

  if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature))) {
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  const event = JSON.parse(body);
  switch (event.event) {
    case "payment.captured":
      console.log("Payment captured:", event.payload.payment.entity.id);
      // TODO: Update order in database
      break;
    case "payment.failed":
      console.log("Payment failed:", event.payload.payment.entity.id);
      break;
  }
  return NextResponse.json({ status: "ok" });
}
''',
            "app/checkout/page.tsx": '''"use client";
import { useState } from "react";
import Script from "next/script";

declare global {
  interface Window { Razorpay: any; }
}

export default function CheckoutPage() {
  const [loading, setLoading] = useState(false);
  const amount = 499;

  const handlePayment = async () => {
    setLoading(true);
    const res = await fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount }),
    });
    const { orderId } = await res.json();

    const options = {
      key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
      amount: amount * 100,
      currency: "INR",
      name: "Your Store",
      order_id: orderId,
      handler: (response: any) => {
        alert(`Payment successful! ID: ${response.razorpay_payment_id}`);
      },
      prefill: { name: "Customer", email: "test@example.com", contact: "9876543210" },
      theme: { color: "#528FF0" },
    };
    new window.Razorpay(options).open();
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <Script src="https://checkout.razorpay.com/v1/checkout.js" />
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <h1 className="text-2xl font-bold mb-4">Checkout</h1>
        <p className="text-gray-600 mb-6">Amount: INR {amount}</p>
        <button onClick={handlePayment} disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Processing..." : `Pay INR ${amount}`}
        </button>
      </div>
    </div>
  );
}
''',
        },
    },
    "django-shiprocket": {
        "id": "django-shiprocket",
        "title": "Django + Shiprocket Shipping",
        "framework": "Django 5",
        "apis": ["/shiprocket/shiprocket-api"],
        "description": "Django project with Shiprocket shipping: order creation, AWB assignment, and shipment tracking.",
        "setup_instructions": [
            "pip install django requests",
            "django-admin startproject myshop && cd myshop",
            "python manage.py startapp shipping",
            "Copy files below, add credentials to settings.py",
            "python manage.py runserver",
        ],
        "files": {
            "shipping/shiprocket_client.py": '''"""Shiprocket API client for Django."""
import requests
from django.conf import settings


class ShiprocketClient:
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"

    def __init__(self):
        self.token = None

    def authenticate(self) -> str:
        response = requests.post(f"{self.BASE_URL}/auth/login", json={
            "email": settings.SHIPROCKET_EMAIL,
            "password": settings.SHIPROCKET_PASSWORD,
        })
        response.raise_for_status()
        self.token = response.json()["token"]
        return self.token

    @property
    def headers(self) -> dict:
        if not self.token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def create_order(self, order_data: dict) -> dict:
        resp = requests.post(f"{self.BASE_URL}/orders/create/adhoc", json=order_data, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def assign_awb(self, shipment_id: int) -> dict:
        resp = requests.post(f"{self.BASE_URL}/courier/assign/awb",
                             json={"shipment_id": shipment_id}, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def track_shipment(self, awb_code: str) -> dict:
        resp = requests.get(f"{self.BASE_URL}/courier/track/awb/{awb_code}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()


shiprocket = ShiprocketClient()
''',
            "shipping/views.py": '''import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .shiprocket_client import shiprocket


@csrf_exempt
@require_POST
def create_shipment(request):
    data = json.loads(request.body)
    result = shiprocket.create_order({
        "order_id": data["order_id"],
        "order_date": data["order_date"],
        "pickup_location": "Primary",
        "billing_customer_name": data["customer_name"],
        "billing_address": data["address"],
        "billing_city": data["city"],
        "billing_pincode": data["pincode"],
        "billing_state": data["state"],
        "billing_country": "India",
        "billing_phone": data["phone"],
        "shipping_is_billing": True,
        "order_items": data["items"],
        "payment_method": data.get("payment_method", "Prepaid"),
        "sub_total": data["subtotal"],
        "length": 20, "breadth": 15, "height": 10, "weight": 0.5,
    })
    if "shipment_id" in result:
        result["awb"] = shiprocket.assign_awb(result["shipment_id"])
    return JsonResponse(result)


@require_GET
def track_shipment(request, awb_code):
    return JsonResponse(shiprocket.track_shipment(awb_code))
''',
            "shipping/urls.py": '''from django.urls import path
from . import views

urlpatterns = [
    path("shipments/create/", views.create_shipment),
    path("shipments/track/<str:awb_code>/", views.track_shipment),
]
''',
        },
    },
    "express-msg91": {
        "id": "express-msg91",
        "title": "Express.js + MSG91 OTP",
        "framework": "Express.js",
        "apis": ["/msg91/msg91-api"],
        "description": "Express.js OTP verification with MSG91: send, verify, and resend endpoints with input validation.",
        "setup_instructions": [
            "mkdir my-otp-app && cd my-otp-app && npm init -y",
            "npm install express axios dotenv",
            "Copy files below, add MSG91 credentials to .env",
            "node server.js",
        ],
        "files": {
            ".env": "MSG91_AUTH_KEY=your_auth_key\nMSG91_TEMPLATE_ID=your_template_id\nPORT=3000\n",
            "server.js": '''require("dotenv").config();
const express = require("express");
const { sendOTP, verifyOTP, resendOTP } = require("./msg91");

const app = express();
app.use(express.json());

app.post("/api/otp/send", async (req, res) => {
  try {
    const { mobile } = req.body;
    if (!mobile || !/^[6-9]\\d{9}$/.test(mobile)) {
      return res.status(400).json({ error: "Valid 10-digit Indian mobile required" });
    }
    const result = await sendOTP(mobile);
    res.json({ success: true, ...result });
  } catch (error) {
    res.status(500).json({ error: "Failed to send OTP" });
  }
});

app.post("/api/otp/verify", async (req, res) => {
  try {
    const { mobile, otp } = req.body;
    if (!mobile || !otp) return res.status(400).json({ error: "mobile and otp required" });
    const result = await verifyOTP(mobile, otp);
    if (result.type === "success") {
      res.json({ success: true, message: "OTP verified" });
    } else {
      res.status(400).json({ success: false, message: "Invalid OTP" });
    }
  } catch (error) {
    res.status(500).json({ error: "Verification failed" });
  }
});

app.post("/api/otp/resend", async (req, res) => {
  try {
    const { mobile, retryType = "text" } = req.body;
    const result = await resendOTP(mobile, retryType);
    res.json({ success: true, ...result });
  } catch (error) {
    res.status(500).json({ error: "Failed to resend OTP" });
  }
});

app.listen(process.env.PORT || 3000, () => console.log("Server running"));
''',
            "msg91.js": '''const axios = require("axios");
const AUTH_KEY = process.env.MSG91_AUTH_KEY;
const TEMPLATE_ID = process.env.MSG91_TEMPLATE_ID;
const BASE = "https://control.msg91.com/api/v5";

async function sendOTP(mobile) {
  const { data } = await axios.post(`${BASE}/otp`, {
    template_id: TEMPLATE_ID, mobile: `91${mobile}`, otp_length: 6, otp_expiry: 5,
  }, { headers: { authkey: AUTH_KEY } });
  return data;
}

async function verifyOTP(mobile, otp) {
  const { data } = await axios.get(`${BASE}/otp/verify`, {
    params: { mobile: `91${mobile}`, otp },
    headers: { authkey: AUTH_KEY },
  });
  return data;
}

async function resendOTP(mobile, retryType = "text") {
  const { data } = await axios.post(`${BASE}/otp/retry`, {
    mobile: `91${mobile}`, retrytype: retryType,
  }, { headers: { authkey: AUTH_KEY } });
  return data;
}

module.exports = { sendOTP, verifyOTP, resendOTP };
''',
        },
    },
    "flask-gstn": {
        "id": "flask-gstn",
        "title": "Flask + GSTN E-Invoice",
        "framework": "Flask",
        "apis": ["/gstn/gst-api"],
        "description": "Flask app for GST e-invoicing via a GSP: IRN generation, cancellation, and e-way bill linking.",
        "setup_instructions": [
            "pip install flask requests python-dotenv",
            "Copy files below, add GSP credentials to .env",
            "flask run",
        ],
        "files": {
            ".env": (
                "GSP_BASE_URL=https://api.mastergst.com\n"
                "GSP_CLIENT_ID=your_client_id\n"
                "GSP_CLIENT_SECRET=your_client_secret\n"
                "GSP_EMAIL=accounts@yourcompany.com\n"
                "GSTIN=29AABCT1332L1ZL\n"
            ),
            "app.py": '''"""Flask app for GSTN E-Invoice generation."""
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from gstn_client import GSTNClient

load_dotenv()
app = Flask(__name__)
gstn = GSTNClient(
    base_url=os.environ["GSP_BASE_URL"],
    client_id=os.environ["GSP_CLIENT_ID"],
    client_secret=os.environ["GSP_CLIENT_SECRET"],
    email=os.environ["GSP_EMAIL"],
    gstin=os.environ["GSTIN"],
)

@app.route("/api/einvoice/generate", methods=["POST"])
def generate_einvoice():
    try:
        result = gstn.generate_irn(request.json)
        return jsonify({"success": True, "irn": result["Irn"], "ack_no": result["AckNo"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/einvoice/cancel", methods=["POST"])
def cancel_einvoice():
    data = request.json
    try:
        result = gstn.cancel_irn(data["irn"], data.get("reason_code", "2"), data.get("reason", "Data entry mistake"))
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
''',
            "gstn_client.py": '''"""GSTN E-Invoice client via GSP (GST Suvidha Provider)."""
import requests
from datetime import datetime


class GSTNClient:
    def __init__(self, base_url, client_id, client_secret, email, gstin):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.email = email
        self.gstin = gstin
        self._token = None

    def _authenticate(self):
        resp = requests.post(f"{self.base_url}/einvoice/authenticate", params={
            "email": self.email, "gstin": self.gstin,
            "client_id": self.client_id, "client_secret": self.client_secret,
        })
        resp.raise_for_status()
        data = resp.json()
        if data.get("status_cd") != "1":
            raise Exception(f"GSP auth failed: {data}")
        self._token = data["data"]["AuthToken"]

    @property
    def headers(self):
        if not self._token:
            self._authenticate()
        return {"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}

    def generate_irn(self, invoice_data):
        payload = {
            "Version": "1.1",
            "TranDtls": {"TaxSch": "GST", "SupTyp": invoice_data.get("supply_type", "B2B")},
            "DocDtls": {
                "Typ": "INV",
                "No": invoice_data.get("invoice_no", f"INV-{datetime.now().strftime('%Y%m%d')}-001"),
                "Dt": invoice_data.get("invoice_date", datetime.now().strftime("%d/%m/%Y")),
            },
            "SellerDtls": invoice_data.get("seller", {}),
            "BuyerDtls": invoice_data.get("buyer", {}),
            "ItemList": invoice_data.get("items", []),
            "ValDtls": invoice_data.get("values", {}),
        }
        resp = requests.post(
            f"{self.base_url}/einvoice/type/GENERATE_IRN/version/V1_03",
            json=payload, headers=self.headers,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("status_cd") != "1":
            raise Exception(f"IRN generation failed: {result.get('error')}")
        return result["data"]

    def cancel_irn(self, irn, reason_code="2", reason="Data entry mistake"):
        resp = requests.post(
            f"{self.base_url}/einvoice/type/CANCEL/version/V1_03",
            json={"Irn": irn, "CnlRsn": reason_code, "CnlRem": reason},
            headers=self.headers,
        )
        return resp.json()
''',
        },
    },
    "nextjs-ondc": {
        "id": "nextjs-ondc",
        "title": "Next.js + ONDC Buyer App",
        "framework": "Next.js 15",
        "apis": ["/ondc/protocol-specs"],
        "description": "ONDC buyer app with Beckn Protocol: search, select, and confirm flows with Ed25519 signing.",
        "setup_instructions": [
            "npx create-next-app@latest my-ondc-app --typescript --tailwind --app",
            "cd my-ondc-app && npm install tweetnacl tweetnacl-util",
            "Copy files below, add ONDC credentials to .env.local",
            "npm run dev",
        ],
        "files": {
            ".env.local": (
                "ONDC_BAP_ID=your-buyer-app.com\n"
                "ONDC_BAP_URI=https://your-buyer-app.com/api/ondc\n"
                "ONDC_GATEWAY_URL=https://staging.gateway.ondc.org\n"
                "ONDC_PRIVATE_KEY=your_ed25519_private_key_base64\n"
            ),
            "lib/ondc/client.ts": '''import nacl from "tweetnacl";
import { decodeBase64, encodeBase64 } from "tweetnacl-util";

const BAP_ID = process.env.ONDC_BAP_ID!;
const BAP_URI = process.env.ONDC_BAP_URI!;
const GATEWAY = process.env.ONDC_GATEWAY_URL!;
const PRIVATE_KEY = process.env.ONDC_PRIVATE_KEY!;

function signRequest(body: string): string {
  const keyPair = nacl.sign.keyPair.fromSecretKey(decodeBase64(PRIVATE_KEY));
  const sig = nacl.sign.detached(new TextEncoder().encode(body), keyPair.secretKey);
  return encodeBase64(sig);
}

export async function searchONDC(item: string, city: string, gps: string) {
  const body = {
    context: {
      domain: "nic2004:52110", action: "search", country: "IND", city,
      core_version: "1.2.0", bap_id: BAP_ID, bap_uri: BAP_URI,
      transaction_id: crypto.randomUUID(), message_id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
    },
    message: {
      intent: {
        item: { descriptor: { name: item } },
        fulfillment: { end: { location: { gps } } },
      },
    },
  };
  const bodyStr = JSON.stringify(body);
  const signature = signRequest(bodyStr);
  const resp = await fetch(`${GATEWAY}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Signature keyId="${BAP_ID}|key1|ed25519",algorithm="ed25519",signature="${signature}"`,
    },
    body: bodyStr,
  });
  return { status: resp.status, transactionId: body.context.transaction_id };
}
''',
            "app/api/ondc/on_search/route.ts": '''import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const payload = await request.json();
  const providers = payload.message?.catalog?.["bpp/providers"] || [];
  const items = providers.flatMap((p: any) =>
    (p.items || []).map((item: any) => ({
      provider: p.descriptor?.name,
      name: item.descriptor?.name,
      price: item.price?.value,
      itemId: item.id,
      providerId: p.id,
    }))
  );
  console.log(`Received ${items.length} items for txn ${payload.context?.transaction_id}`);
  return NextResponse.json({ context: payload.context, message: { ack: { status: "ACK" } } });
}
''',
        },
    },
}


# ─── Endpoints ───────────────────────────────────────────────────────────────


@router.get("", response_model=StarterListResponse)
async def list_starters() -> StarterListResponse:
    """List all available framework starter templates."""
    if not flags.FRAMEWORK_STARTERS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    summaries = [
        StarterSummary(
            id=s["id"],
            title=s["title"],
            framework=s["framework"],
            apis=s["apis"],
            description=s["description"],
            file_count=len(s["files"]),
        )
        for s in STARTERS.values()
    ]
    return StarterListResponse(starters=summaries, total=len(summaries))


@router.get("/{starter_id}", response_model=StarterDetail)
async def get_starter(starter_id: str) -> StarterDetail:
    """Get a framework starter with full file tree and code."""
    if not flags.FRAMEWORK_STARTERS:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    starter = STARTERS.get(starter_id)
    if not starter:
        raise HTTPException(
            status_code=404,
            detail=f"Starter '{starter_id}' not found. Use GET /v1/starters to list available starters.",
        )

    return StarterDetail(
        id=starter["id"],
        title=starter["title"],
        framework=starter["framework"],
        apis=starter["apis"],
        description=starter["description"],
        setup_instructions=starter.get("setup_instructions", []),
        files=starter["files"],
    )
