"""Community Q&A — questions and answers per library."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/community", tags=["community"])


# ── Pydantic Models ──────────────────────────────────────────────


class Question(BaseModel):
    """A community question about a library."""

    id: str = Field(..., description="Unique question ID")
    library_id: str
    title: str
    body: str
    tags: list[str] = Field(default_factory=list)
    answers_count: int = Field(default=0)
    upvotes: int = Field(default=0)
    asked_by: str = Field(default="anonymous")
    asked_at: str


class Answer(BaseModel):
    """An answer to a community question."""

    id: str = Field(..., description="Unique answer ID")
    question_id: str
    body: str
    upvotes: int = Field(default=0)
    answered_by: str = Field(default="anonymous")
    answered_at: str
    accepted: bool = Field(default=False)


class QuestionListResponse(BaseModel):
    """Response containing questions for a library."""

    library_id: str | None
    questions: list[Question]
    total: int


class AskQuestionRequest(BaseModel):
    """Request to ask a new community question."""

    library_id: str = Field(
        ..., description="Canonical library ID, e.g. /razorpay/razorpay-sdk"
    )
    title: str = Field(
        ..., description="Question title", min_length=10, max_length=200
    )
    body: str = Field(
        ...,
        description="Detailed question body with context and code if applicable",
        min_length=20,
        max_length=10000,
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
        max_length=5,
    )


class AskQuestionResponse(BaseModel):
    """Response after asking a question."""

    id: str
    library_id: str
    title: str
    asked: bool


class SubmitAnswerRequest(BaseModel):
    """Request to answer an existing question."""

    question_id: str = Field(..., description="ID of the question to answer")
    body: str = Field(
        ...,
        description="Answer body with explanation and code if applicable",
        min_length=20,
        max_length=10000,
    )


class SubmitAnswerResponse(BaseModel):
    """Response after submitting an answer."""

    id: str
    question_id: str
    answered: bool


# ── Pre-seeded Q&A Data ──────────────────────────────────────────

_questions: dict[str, dict] = {}
_answers: dict[str, dict] = {}


def _seed_data() -> None:
    """Pre-seed the in-memory store with realistic questions and answers."""
    seed_questions = [
        # Razorpay
        {
            "id": "q-rzp-001",
            "library_id": "/razorpay/razorpay-sdk",
            "title": "How to test webhooks locally during development?",
            "body": (
                "I'm building a Razorpay integration and need to test webhook "
                "events (payment.captured, payment.failed) on my local machine. "
                "Razorpay requires a public URL for webhooks. What's the best "
                "approach for local development?\n\n"
                "I've tried using the Dashboard test mode but it still needs a "
                "reachable URL."
            ),
            "tags": ["webhooks", "testing", "local-dev"],
            "upvotes": 34,
            "asked_by": "dev_mumbai",
            "asked_at": "2026-02-15T10:30:00Z",
        },
        {
            "id": "q-rzp-002",
            "library_id": "/razorpay/razorpay-sdk",
            "title": "Subscription vs recurring payment — when to use which?",
            "body": (
                "Razorpay offers both Subscriptions API and Recurring Payments "
                "(emandate). I'm building a SaaS product with monthly billing. "
                "Which one should I use?\n\n"
                "My use case: fixed monthly amount, card/UPI autopay, ability "
                "to upgrade/downgrade plans mid-cycle."
            ),
            "tags": ["subscriptions", "recurring", "billing"],
            "upvotes": 28,
            "asked_by": "saas_builder",
            "asked_at": "2026-02-20T14:15:00Z",
        },
        {
            "id": "q-rzp-003",
            "library_id": "/razorpay/razorpay-sdk",
            "title": "How to handle payment.captured vs order.paid webhooks?",
            "body": (
                "I receive both payment.captured and order.paid webhooks for the "
                "same transaction. Which one should I use to confirm the order "
                "in my system? Is there a race condition risk?"
            ),
            "tags": ["webhooks", "payments", "order-flow"],
            "upvotes": 22,
            "asked_by": "ecom_dev",
            "asked_at": "2026-03-01T09:00:00Z",
        },
        # Zerodha
        {
            "id": "q-zrd-001",
            "library_id": "/zerodha/kite-api",
            "title": "How to handle daily token refresh for automated trading?",
            "body": (
                "Kite Connect access tokens expire every day at 6 AM IST. For "
                "my algo trading bot that runs continuously, I need to automate "
                "the token refresh. The login flow requires browser-based OAuth "
                "which makes headless automation difficult.\n\n"
                "Has anyone successfully automated this with TOTP-based login?"
            ),
            "tags": ["authentication", "algo-trading", "automation"],
            "upvotes": 56,
            "asked_by": "algo_trader_42",
            "asked_at": "2026-01-25T08:00:00Z",
        },
        {
            "id": "q-zrd-002",
            "library_id": "/zerodha/kite-api",
            "title": "WebSocket reconnection strategy for live market data?",
            "body": (
                "My Kite WebSocket connection drops intermittently during high "
                "volatility periods. What's a robust reconnection strategy?\n\n"
                "Current setup: I'm using kiteconnect.KiteTicker with on_close "
                "callback, but sometimes the reconnection fails and I miss "
                "tick data for several minutes."
            ),
            "tags": ["websocket", "market-data", "reliability"],
            "upvotes": 43,
            "asked_by": "quant_dev",
            "asked_at": "2026-02-10T11:30:00Z",
        },
        {
            "id": "q-zrd-003",
            "library_id": "/zerodha/kite-api",
            "title": "How to get historical data for backtesting strategies?",
            "body": (
                "I need minute-level OHLCV data for NIFTY 50 stocks going back "
                "2 years for backtesting. Kite historical data API has rate limits "
                "and max 60-day windows. What's the most efficient way to download "
                "all the data I need?"
            ),
            "tags": ["historical-data", "backtesting", "rate-limits"],
            "upvotes": 38,
            "asked_by": "backtest_dev",
            "asked_at": "2026-02-28T16:00:00Z",
        },
        # ONDC
        {
            "id": "q-ondc-001",
            "library_id": "/ondc/protocol-specs",
            "title": "How does catalog search work in ONDC retail domain?",
            "body": (
                "I'm building a buyer app for ONDC retail. When my app sends "
                "a /search request to the gateway, how does the catalog discovery "
                "work? Does the gateway broadcast to all seller apps? How do I "
                "handle the async /on_search responses?\n\n"
                "The Beckn spec mentions 'intent' object but the ONDC retail "
                "spec has additional requirements."
            ),
            "tags": ["search", "catalog", "buyer-app", "retail"],
            "upvotes": 31,
            "asked_by": "ondc_builder",
            "asked_at": "2026-02-05T13:00:00Z",
        },
        {
            "id": "q-ondc-002",
            "library_id": "/ondc/protocol-specs",
            "title": "Ed25519 signing implementation — complete working example?",
            "body": (
                "The ONDC docs explain the Authorization header format but I "
                "can't get the signing to work. I'm using PyNaCl in Python.\n\n"
                "My signature keeps getting rejected with 'Invalid signature' "
                "error. I suspect the signing string construction is wrong. "
                "Can someone share a complete working example including the "
                "Blake2b digest computation?"
            ),
            "tags": ["signing", "ed25519", "authentication", "python"],
            "upvotes": 47,
            "asked_by": "crypto_confused",
            "asked_at": "2026-01-30T10:45:00Z",
        },
        {
            "id": "q-ondc-003",
            "library_id": "/ondc/protocol-specs",
            "title": "How to handle ONDC order cancellation flow correctly?",
            "body": (
                "I need to implement order cancellation for my seller app. "
                "The flow seems complex: buyer sends /cancel, seller gets "
                "/on_cancel callback, then needs to handle refund. What are "
                "the mandatory cancellation reason codes, and when does the "
                "buyer vs seller initiate cancellation?"
            ),
            "tags": ["cancellation", "seller-app", "order-flow"],
            "upvotes": 25,
            "asked_by": "seller_app_dev",
            "asked_at": "2026-03-10T15:20:00Z",
        },
    ]

    seed_answers = [
        # Answer for Razorpay webhook testing
        {
            "id": "a-rzp-001-1",
            "question_id": "q-rzp-001",
            "body": (
                "Use **ngrok** to expose your local server:\n\n"
                "```bash\n"
                "# Install ngrok\n"
                "brew install ngrok  # or download from ngrok.com\n\n"
                "# Start your local server\n"
                "python manage.py runserver 8000\n\n"
                "# In another terminal, expose port 8000\n"
                "ngrok http 8000\n"
                "# You'll get a URL like: https://abc123.ngrok-free.app\n"
                "```\n\n"
                "Then set the webhook URL in Razorpay Dashboard > Settings > "
                "Webhooks to `https://abc123.ngrok-free.app/razorpay/webhook`.\n\n"
                "For automated testing, use the Razorpay Dashboard 'Send Test "
                "Webhook' button — it sends a simulated event to your URL.\n\n"
                "Alternative: Razorpay also supports webhook event replay from "
                "the Dashboard > Events section. Click any past event and hit "
                "'Resend' to replay it to your endpoint."
            ),
            "upvotes": 21,
            "answered_by": "fullstack_pro",
            "answered_at": "2026-02-15T12:00:00Z",
            "accepted": True,
        },
        # Answer for Subscription vs recurring
        {
            "id": "a-rzp-002-1",
            "question_id": "q-rzp-002",
            "body": (
                "For a SaaS product, use **Subscriptions API**. Here's why:\n\n"
                "**Subscriptions API** (recommended for your case):\n"
                "- Built for fixed recurring billing (SaaS, memberships)\n"
                "- Supports plan upgrade/downgrade via `subscription.update()`\n"
                "- Handles proration automatically\n"
                "- Supports card, UPI autopay, and emandate\n"
                "- Built-in retry logic for failed charges (3 retries over 7 days)\n\n"
                "**Recurring Payments (emandate/UPI autopay)**:\n"
                "- Lower-level API for custom recurring logic\n"
                "- You manage billing cycle, retry, proration yourself\n"
                "- Better for variable amounts (utility bills, EMIs)\n\n"
                "```python\n"
                "# Subscriptions API example\n"
                "plan = razorpay_client.plan.create({\n"
                "    'period': 'monthly',\n"
                "    'interval': 1,\n"
                "    'item': {\n"
                "        'name': 'Pro Plan',\n"
                "        'amount': 39900,  # INR 399 in paise\n"
                "        'currency': 'INR'\n"
                "    }\n"
                "})\n\n"
                "subscription = razorpay_client.subscription.create({\n"
                "    'plan_id': plan['id'],\n"
                "    'total_count': 12,  # 12 months\n"
                "    'quantity': 1\n"
                "})\n"
                "```"
            ),
            "upvotes": 18,
            "answered_by": "billing_expert",
            "answered_at": "2026-02-21T09:30:00Z",
            "accepted": True,
        },
        # Answer for Zerodha token refresh
        {
            "id": "a-zrd-001-1",
            "question_id": "q-zrd-001",
            "body": (
                "Here's the TOTP-based automation approach:\n\n"
                "```python\n"
                "import pyotp\n"
                "from kiteconnect import KiteConnect\n"
                "import requests\n\n"
                "def auto_login(api_key: str, api_secret: str,\n"
                "               user_id: str, password: str,\n"
                "               totp_secret: str) -> str:\n"
                "    \"\"\"Automated Kite login using TOTP.\"\"\"\n"
                "    kite = KiteConnect(api_key=api_key)\n\n"
                "    # Step 1: Submit credentials to Kite login\n"
                "    session = requests.Session()\n"
                "    login_resp = session.post(\n"
                "        'https://kite.zerodha.com/api/login',\n"
                "        data={'user_id': user_id, 'password': password}\n"
                "    )\n"
                "    request_id = login_resp.json()['data']['request_id']\n\n"
                "    # Step 2: Submit TOTP\n"
                "    totp = pyotp.TOTP(totp_secret)\n"
                "    twofa_resp = session.post(\n"
                "        'https://kite.zerodha.com/api/twofa',\n"
                "        data={\n"
                "            'user_id': user_id,\n"
                "            'request_id': request_id,\n"
                "            'twofa_value': totp.now(),\n"
                "            'twofa_type': 'totp'\n"
                "        }\n"
                "    )\n\n"
                "    # Step 3: Extract request_token from redirect\n"
                "    # ... process the response to get request_token\n"
                "    request_token = extract_request_token(twofa_resp)\n\n"
                "    # Step 4: Generate access token\n"
                "    data = kite.generate_session(request_token, api_secret)\n"
                "    return data['access_token']\n"
                "```\n\n"
                "Set up TOTP: Go to Zerodha Console > Security > Enable TOTP. "
                "Save the TOTP secret key. Use `pyotp.TOTP(secret).now()` to "
                "generate codes.\n\n"
                "Run this as a cron job at 8:30 AM IST (before market opens at 9:15)."
            ),
            "upvotes": 35,
            "answered_by": "algo_veteran",
            "answered_at": "2026-01-26T07:00:00Z",
            "accepted": True,
        },
        # Answer for ONDC Ed25519 signing
        {
            "id": "a-ondc-002-1",
            "question_id": "q-ondc-002",
            "body": (
                "Here's a complete working example. The key gotcha is the "
                "signing string format — each header on a new line, and the "
                "digest uses Blake2b-512.\n\n"
                "```python\n"
                "import base64\n"
                "import hashlib\n"
                "import json\n"
                "import time\n"
                "from nacl.signing import SigningKey\n\n"
                "def create_auth_header(\n"
                "    body: dict,\n"
                "    private_key_b64: str,\n"
                "    subscriber_id: str,\n"
                "    unique_key_id: str\n"
                ") -> str:\n"
                "    # 1. Serialize body to JSON (no spaces after separators)\n"
                "    body_str = json.dumps(body, separators=(',', ':'))\n\n"
                "    # 2. Blake2b-512 digest\n"
                "    digest = hashlib.blake2b(\n"
                "        body_str.encode('utf-8'), digest_size=64\n"
                "    ).digest()\n"
                "    digest_b64 = base64.b64encode(digest).decode()\n\n"
                "    # 3. Build signing string\n"
                "    created = int(time.time())\n"
                "    expires = created + 300\n"
                "    signing_string = (\n"
                "        f'(created): {created}\\n'\n"
                "        f'(expires): {expires}\\n'\n"
                "        f'digest: BLAKE-512={digest_b64}'\n"
                "    )\n\n"
                "    # 4. Sign with Ed25519\n"
                "    seed = base64.b64decode(private_key_b64)\n"
                "    signing_key = SigningKey(seed)\n"
                "    signed = signing_key.sign(signing_string.encode('utf-8'))\n"
                "    sig_b64 = base64.b64encode(signed.signature).decode()\n\n"
                "    # 5. Build header\n"
                "    key_id = f'{subscriber_id}|{unique_key_id}|ed25519'\n"
                "    return (\n"
                "        f'Signature keyId=\"{key_id}\",'\n"
                "        f'algorithm=\"ed25519\",'\n"
                "        f'created=\"{created}\",'\n"
                "        f'expires=\"{expires}\",'\n"
                "        f'headers=\"(created) (expires) digest\",'\n"
                "        f'signature=\"{sig_b64}\"'\n"
                "    )\n"
                "```\n\n"
                "**Important**: The `private_key_b64` must be the raw 32-byte "
                "Ed25519 seed, NOT the full 64-byte private key. If you "
                "generated keys with `openssl`, extract the seed:\n\n"
                "```python\n"
                "# Generate key pair\n"
                "signing_key = SigningKey.generate()\n"
                "private_key_b64 = base64.b64encode(signing_key.encode()).decode()\n"
                "public_key_b64 = base64.b64encode(\n"
                "    signing_key.verify_key.encode()\n"
                ").decode()\n"
                "# Register public_key_b64 in ONDC registry\n"
                "```"
            ),
            "upvotes": 39,
            "answered_by": "ondc_certified",
            "answered_at": "2026-02-01T16:30:00Z",
            "accepted": True,
        },
    ]

    for q in seed_questions:
        # Count answers for this question
        q_answers = [a for a in seed_answers if a["question_id"] == q["id"]]
        q["answers_count"] = len(q_answers)
        _questions[q["id"]] = q

    for a in seed_answers:
        _answers[a["id"]] = a


# Initialize seed data on module load
_seed_data()


# ── Endpoints ────────────────────────────────────────────────────


@router.get("/questions", response_model=QuestionListResponse)
async def list_questions(
    library_id: str | None = Query(
        None, description="Filter by library ID, e.g. /razorpay/razorpay-sdk"
    ),
    tag: str | None = Query(None, description="Filter by tag"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
) -> QuestionListResponse:
    """
    Get community questions, optionally filtered by library.

    Returns questions sorted by upvotes (descending). Includes answer count
    for each question to help users find already-answered questions.

    Args:
        library_id: Optional filter by canonical library ID.
        tag: Optional filter by tag.
        limit: Maximum number of questions to return.
    """
    if not flags.COMMUNITY_QA:
        raise HTTPException(
            status_code=403,
            detail="Community Q&A is disabled. Set FEATURE_COMMUNITY_QA=true to enable.",
        )

    questions = list(_questions.values())

    if library_id:
        questions = [q for q in questions if q["library_id"] == library_id]

    if tag:
        questions = [q for q in questions if tag in q.get("tags", [])]

    # Sort by upvotes descending
    questions.sort(key=lambda q: q.get("upvotes", 0), reverse=True)
    questions = questions[:limit]

    logger.info(
        "Serving community questions",
        extra={"library_id": library_id, "tag": tag, "count": len(questions)},
    )

    return QuestionListResponse(
        library_id=library_id,
        questions=[Question(**q) for q in questions],
        total=len(questions),
    )


@router.get("/questions/{question_id}", response_model=Question)
async def get_question(question_id: str) -> Question:
    """
    Get a single question by ID.

    Args:
        question_id: The unique question ID.
    """
    if not flags.COMMUNITY_QA:
        raise HTTPException(
            status_code=403,
            detail="Community Q&A is disabled. Set FEATURE_COMMUNITY_QA=true to enable.",
        )

    question = _questions.get(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")

    return Question(**question)


@router.get("/questions/{question_id}/answers", response_model=list[Answer])
async def get_answers(question_id: str) -> list[Answer]:
    """
    Get all answers for a specific question.

    Args:
        question_id: The unique question ID.
    """
    if not flags.COMMUNITY_QA:
        raise HTTPException(
            status_code=403,
            detail="Community Q&A is disabled. Set FEATURE_COMMUNITY_QA=true to enable.",
        )

    if question_id not in _questions:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")

    answers = [
        Answer(**a)
        for a in _answers.values()
        if a["question_id"] == question_id
    ]
    # Accepted answers first, then by upvotes
    answers.sort(key=lambda a: (-int(a.accepted), -a.upvotes))

    return answers


@router.post("/questions", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest) -> AskQuestionResponse:
    """
    Ask a new community question about a library.

    Questions are stored in memory for MVP. In production, these would be
    persisted to the database with full user authentication and moderation.

    Args:
        request: Question details including library ID, title, body, and tags.
    """
    if not flags.COMMUNITY_QA:
        raise HTTPException(
            status_code=403,
            detail="Community Q&A is disabled. Set FEATURE_COMMUNITY_QA=true to enable.",
        )

    question_id = f"q-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    question = {
        "id": question_id,
        "library_id": request.library_id,
        "title": request.title,
        "body": request.body,
        "tags": request.tags,
        "answers_count": 0,
        "upvotes": 0,
        "asked_by": "anonymous",
        "asked_at": now,
    }
    _questions[question_id] = question

    logger.info(
        "Community question asked",
        extra={
            "question_id": question_id,
            "library_id": request.library_id,
            "title": request.title[:80],
        },
    )

    return AskQuestionResponse(
        id=question_id,
        library_id=request.library_id,
        title=request.title,
        asked=True,
    )


@router.post("/answers", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest) -> SubmitAnswerResponse:
    """
    Answer an existing community question.

    Answers are stored in memory for MVP. In production, these would be
    persisted to the database with user authentication and voting.

    Args:
        request: Answer details including question ID and answer body.
    """
    if not flags.COMMUNITY_QA:
        raise HTTPException(
            status_code=403,
            detail="Community Q&A is disabled. Set FEATURE_COMMUNITY_QA=true to enable.",
        )

    if request.question_id not in _questions:
        raise HTTPException(
            status_code=404,
            detail=f"Question '{request.question_id}' not found.",
        )

    answer_id = f"a-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    answer = {
        "id": answer_id,
        "question_id": request.question_id,
        "body": request.body,
        "upvotes": 0,
        "answered_by": "anonymous",
        "answered_at": now,
        "accepted": False,
    }
    _answers[answer_id] = answer

    # Update answer count on the question
    _questions[request.question_id]["answers_count"] = sum(
        1 for a in _answers.values() if a["question_id"] == request.question_id
    )

    logger.info(
        "Community answer submitted",
        extra={
            "answer_id": answer_id,
            "question_id": request.question_id,
        },
    )

    return SubmitAnswerResponse(
        id=answer_id,
        question_id=request.question_id,
        answered=True,
    )
