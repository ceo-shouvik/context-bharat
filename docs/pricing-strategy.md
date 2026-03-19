# contextBharat — Pricing Strategy: Pay-Per-Use / Credits

## TL;DR

**Drop subscriptions. Go with prepaid credits (Anthropic-style) + generous free tier.**

- Free: 50 credits/day (no signup needed) + 200 credits/day (with free account)
- Paid: Buy credit packs — ₹99 for 5,000 credits, ₹399 for 25,000 credits, ₹999 for 100,000 credits
- 1 API query = 1 credit (simple, predictable)
- Credits never expire (unlike Anthropic's 1-year expiry)
- Implement with Razorpay (India) + Stripe (international)

---

## Why Pay-Per-Use Over Subscriptions

| Factor | Subscription (₹399/mo) | Pay-Per-Use (Credits) |
|--------|------------------------|----------------------|
| **User friction** | High — commitment upfront | Low — pay only what you use |
| **Casual users** | Lost — won't pay ₹399 for 10 queries/mo | Retained — buy ₹99 pack, lasts months |
| **Heavy users** | Underpriced — unlimited at ₹399 | Fair — they pay proportionally |
| **Revenue predictability** | Higher | Lower (but grows with usage) |
| **India developer psychology** | "Another subscription I'll forget" | "I control my spend" |
| **Student/hobbyist friendly** | No — ₹399 is steep for students | Yes — ₹99 pack for a semester |

**Key insight:** Indian developers are price-sensitive and subscription-fatigued. Credits feel like "buying what I need" not "paying whether I use it or not."

---

## How Industry Leaders Do It

### Anthropic (Claude API)
- Prepaid credits, charged per million tokens (input/output separately)
- $5 free credits for new users
- Credits expire after 1 year
- Auto-reload option available

### OpenAI
- Postpaid usage-based (charged monthly for what you used)
- Per-million-token pricing
- Free tier with rate limits

### Upstash (Redis)
- Pure per-request: $0.2 per 100K commands
- Price cap at $360/mo (prevents bill shock)
- Zero cost when idle

### Vercel
- Included allocations per plan + overage billing
- Edge requests: $2 per million after included quota

### Zerodha Kite API
- Free for personal use
- Charges per order placed (₹20/order for non-equity)
- No subscription fee for API access

---

## Proposed Pricing Model

### Free Tier (No Signup)
- **50 credits/day** (50 queries)
- Top 30 libraries only
- English only
- Rate limited: 10 queries/minute

### Free Account (Email signup)
- **200 credits/day** (200 queries)
- All libraries
- English only
- Rate limited: 30 queries/minute

### Credit Packs (Prepaid)

| Pack | Credits | Price (INR) | Price (USD) | Per Query | Best For |
|------|---------|-------------|-------------|-----------|----------|
| **Starter** | 5,000 | ₹99 | $1.19 | ₹0.020 | Students, hobbyists |
| **Builder** | 25,000 | ₹399 | $4.79 | ₹0.016 | Indie devs, freelancers |
| **Pro** | 100,000 | ₹999 | $11.99 | ₹0.010 | Startups, daily users |
| **Team** | 500,000 | ₹3,999 | $47.99 | ₹0.008 | Teams, heavy usage |

### Premium Add-ons (Per Credit)
- Hindi / regional language queries: **2 credits** per query (instead of 1)
- Private library indexing: **5 credits** per query against private repos
- Priority queue (faster response): **2 credits** per query

### Credits Policy
- **Credits never expire** (competitive advantage over Anthropic)
- **No auto-reload by default** (prevents surprise charges)
- **Optional auto-reload** when balance drops below threshold
- **Usage dashboard** with real-time balance
- **Email alerts** at 20%, 10%, 0% balance remaining

---

## Unit Economics

### Our Cost Per Query
| Component | Cost per query |
|-----------|---------------|
| Cloudflare Worker (MCP) | ~$0 (free tier) |
| Railway (Backend API) | ~₹0.002 |
| Supabase (pgvector search) | ~₹0.001 |
| Upstash (Redis cache hit) | ~₹0.0002 |
| OpenAI (embedding for new queries) | ~₹0.003 |
| Cohere (reranking) | ~₹0.005 |
| **Total cost per query** | **~₹0.011** |

### Margin Per Pack
| Pack | Revenue | Cost (at avg queries) | Margin |
|------|---------|----------------------|--------|
| Starter (5K) | ₹99 | ₹55 | **44%** |
| Builder (25K) | ₹399 | ₹275 | **31%** |
| Pro (100K) | ₹999 | ₹1,100 | **-10%** (loss leader at full usage) |
| Team (500K) | ₹3,999 | ₹5,500 | **-27%** (loss leader) |

**Reality:** Most users won't use 100% of credits. Expected utilization ~40-60%, making all tiers profitable.

---

## Technical Implementation

### Phase 1: Simple (Week 1) — Database-Only Credits

No billing platform needed. Just a credits table.

```sql
-- Add to existing Supabase schema
CREATE TABLE credit_wallets (
    user_id     UUID PRIMARY KEY REFERENCES auth.users(id),
    balance     INTEGER NOT NULL DEFAULT 200,  -- Free signup credits
    total_purchased INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE credit_ledger (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES auth.users(id),
    amount          INTEGER NOT NULL,          -- +ve = credit, -ve = debit
    balance_after   INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,             -- 'purchase', 'query', 'refund', 'free_daily'
    description     TEXT,
    idempotency_key TEXT UNIQUE,               -- Prevents double-billing
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ledger_user_id ON credit_ledger(user_id);
CREATE INDEX idx_ledger_created_at ON credit_ledger(created_at);
```

### Phase 2: Payment Integration (Week 2-3)

**India (Razorpay):**
```python
# backend/app/api/v1/credits.py
@router.post("/purchase")
async def purchase_credits(
    pack: CreditPack,  # "starter" | "builder" | "pro" | "team"
    user: User = Depends(get_current_user),
):
    # Create Razorpay order
    order = razorpay_client.order.create({
        "amount": PACK_PRICES[pack] * 100,  # paise
        "currency": "INR",
        "receipt": f"credits_{user.id}_{pack}",
    })
    return {"order_id": order["id"], "amount": order["amount"]}

# Webhook: Razorpay payment success → add credits
@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):
    # Verify signature, add credits atomically
    await credit_service.add_credits(
        user_id=payment.user_id,
        amount=PACK_CREDITS[pack],
        transaction_type="purchase",
        idempotency_key=payment.id,
    )
```

**International (Stripe):**
```python
# Stripe Checkout session for credit purchase
session = stripe.checkout.Session.create(
    line_items=[{"price": STRIPE_PRICE_IDS[pack], "quantity": 1}],
    mode="payment",  # One-time, not subscription
    success_url="https://contextbharat.com/dashboard?credits=success",
)
```

### Phase 3: Query Metering (Integrated into API)

```python
# backend/app/middleware/credits.py
async def deduct_credits(user_id: str, query_type: str = "standard"):
    cost = QUERY_COSTS.get(query_type, 1)  # 1 for standard, 2 for Hindi, etc.

    # Atomic deduction with optimistic locking
    result = await db.execute(
        update(CreditWallet)
        .where(CreditWallet.user_id == user_id)
        .where(CreditWallet.balance >= cost)
        .values(balance=CreditWallet.balance - cost)
        .returning(CreditWallet.balance)
    )

    if not result.scalar():
        raise InsufficientCreditsError(required=cost)

    # Log to ledger (async, non-blocking)
    await ledger.log(user_id, -cost, "query", idempotency_key=request_id)
```

---

## Migration from Current Subscription Plan

| Old (website/content.md) | New |
|--------------------------|-----|
| Free — ₹0/month, 100 queries/day | Free — 200 credits/day with account |
| Pro — ₹399/month, unlimited | Builder pack — ₹399 for 25,000 credits |
| Team — ₹999/seat/month | Team pack — ₹3,999 for 500,000 credits |

---

## Billing Platform Decision

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **DIY (Supabase + Razorpay)** | Full control, no extra cost, India-native | Build invoicing, receipts, tax yourself | MVP (first 6 months) |
| **Stripe Billing** | Metering built-in, invoicing, tax | No native UPI, international focus | International users |
| **Lago (open-source)** | Self-hosted, processor-agnostic | Setup effort, maintain infra | Post-revenue scale |

### Recommendation: Start with DIY, add Stripe later

**Month 0-6:** Razorpay for payments + DIY credit ledger in Supabase
**Month 6+:** Add Stripe for international users
**Month 12+:** Evaluate Lago if billing complexity grows

---

## Competitive Positioning

| Service | Model | Our Advantage |
|---------|-------|---------------|
| Context7 | $10/mo subscription | We're 80% cheaper per query, no commitment |
| GitHub Copilot | $10-19/mo subscription | We're complementary, not competing |
| Anthropic API | Prepaid credits (expensive) | Same model, 100x cheaper for doc queries |

**Tagline update:** "Pay for what you use. ₹99 gets you started."

---

## Open Questions

1. Should we offer a "monthly credit allowance" plan (₹199/mo for 10K credits auto-refill)?
   - Hybrid between subscription and pay-per-use
   - Predictable revenue + usage-based feel
2. Should team credits be shared across a pool or per-seat?
3. Should we offer bulk discounts for API providers who sponsor their docs?
