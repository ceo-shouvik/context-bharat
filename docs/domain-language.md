# Domain Language

Glossary of terms used throughout this codebase. When you see these terms in code, comments, or discussions — this is what they mean.

---

## Core Concepts

**Library**
Any indexable documentation source. Can be an API (Razorpay), SDK (Zerodha Kite Python), framework (Django), government spec (UPI NPCI), or enterprise tool (Zoho CRM). The atomic unit of our index.

**Library ID**
A canonical, human-readable identifier for a library. Format: `/{owner}/{repo}`. Examples:
- `/razorpay/razorpay-sdk`
- `/npci/upi-specs`
- `/ondc/protocol-specs`
- `/zerodha/kite-api`
- `/zoho/zoho-crm`
- `/vercel/next.js`

**Doc Chunk**
A 512-token slice of documentation text with associated metadata (library ID, section title, URL, language, embedding vector). The unit stored in the vector database.

**Ingestion Run**
A complete pipeline cycle for one library: crawl → extract → chunk → enrich → embed → upsert. Produces a set of doc chunks stored in pgvector.

**Freshness Score**
A 0.0–1.0 score indicating how recently a library's docs were re-indexed. Computed as: `1.0 - (hours_since_last_index / max_staleness_hours)`. Included in API responses so MCP clients can warn users of stale data.

**Token Budget**
The maximum number of tokens the `query-docs` tool will return in a single response. Default: 5000. Configurable per request. Matches Context7's architecture for compatibility.

**MCP Tool**
A function exposed by our MCP server that AI coding assistants can call. We expose two primary tools:
- `resolve-library-id`: maps a library name to its canonical ID
- `query-docs`: retrieves relevant documentation for a library + query

---

## India Stack Terminology

**India Stack**
The suite of government-built digital public infrastructure (DPI) APIs that underpin India's digital economy. Includes UPI, Aadhaar, DigiLocker, GSTN, ONDC, and Account Aggregator.

**DPI (Digital Public Infrastructure)**
Government-built open platforms for digital services. India Stack is India's DPI.

**UPI (Unified Payments Interface)**
Real-time payment protocol built by NPCI. Powers 85%+ of India's retail digital payments. XML-based (not REST). Accessed through PSP banks, not directly.

**NPCI (National Payments Corporation of India)**
The regulatory body that runs UPI, FASTag, BBPS, NACH, RuPay, and other payment infrastructure.

**ONDC (Open Network for Digital Commerce)**
An open, interoperable protocol for e-commerce. Built on Beckn Protocol. Requires Ed25519 crypto signing, DNS verification, async server-to-server architecture.

**Beckn Protocol**
The underlying async, decentralized protocol that ONDC is built on. Defines buyer app ↔ gateway ↔ seller app communication.

**Account Aggregator (AA)**
A framework for consent-based financial data sharing between banks, insurance companies, and apps. Governed by Sahamati. Complex consent flow with 780+ participating FIPs.

**FIP (Financial Information Provider)**
Banks and financial institutions that share data via the Account Aggregator framework.

**GSTN (GST Network)**
The IT backbone of India's Goods and Services Tax system. Provides APIs for GST return filing, invoice management, and e-way bills.

**GSP (GST Suvidha Provider)**
Third-party providers (ClearTax, MasterGST) that abstract GSTN API complexity. Most developers use GSPs rather than GSTN directly.

**ABDM (Ayushman Bharat Digital Mission)**
India's digital health ecosystem. APIs for health records, provider linking, consent management. Complex async architecture with 202 status + webhook callbacks.

**DigiLocker**
Government document wallet. APIs for issuing and verifying documents (Aadhaar, driving license, etc.). Docs are PDFs.

**Aadhaar / eKYC**
India's biometric ID system. eKYC APIs for identity verification. Multi-layer partnership required (ASP → ESP → CCA → UIDAI). No public sandbox.

**ASP (Application Service Provider)**
Companies that integrate with UIDAI's Aadhaar APIs. Requires certification.

**eSign**
Electronic signature using Aadhaar OTP authentication. Legal equivalent of physical signature.

---

## Fintech Terminology

**PG (Payment Gateway)**
Razorpay, Cashfree, PayU, CCAvenue, Paytm PG — companies that process card/UPI payments for merchants.

**PSP (Payment Service Provider)**
Licensed entities that access UPI directly (Paytm, PhonePe, Google Pay). Different from payment gateways.

**BBPS (Bharat Bill Payment System)**
NPCI's bill payment network. Utility bills, loan EMIs, subscription payments.

**NACH (National Automated Clearing House)**
Bank mandate system for recurring payments (EMIs, SIPs).

**eMandate / eNACH**
Digital version of NACH mandates using net banking or Aadhaar OTP.

**Payout**
Transferring money from a business to a beneficiary (vendor payment, salary, refund). Razorpay Payouts, Cashfree Payouts.

**VPA (Virtual Payment Address)**
UPI address like `name@paytm` or `number@upi`. The human-readable UPI identifier.

---

## Trading / Broking Terminology

**Kite API**
Zerodha's trading API. The most used trading API in India. REST-based. WebSocket for live feeds.

**SmartAPI**
Angel One's trading API. Similar to Kite API.

**Algo Trading**
Automated trading using APIs. Heavy Kite/Upstox API users.

**Broker**
Zerodha, Upstox, AngelOne, Groww, Dhan — licensed stock brokers that expose trading APIs.

**SEBI**
Securities and Exchange Board of India. Regulatory authority for trading APIs.

---

## Technical Terminology (Our System)

**Embedding**
A fixed-length vector (1536 dimensions for text-embedding-3-small) representing the semantic meaning of a doc chunk.

**Cosine Similarity**
The primary similarity metric used for vector search. Measures the angle between two embedding vectors.

**Hybrid Search**
Combining BM25 keyword search with cosine similarity vector search, then merging results. More accurate than either alone.

**Reranking**
A second pass over search results using a cross-encoder model (Cohere Rerank) to more accurately score relevance. Improves top-10 quality significantly.

**Cross-Encoder**
A model that takes (query, document) pairs and scores their relevance. More accurate but slower than bi-encoder (embedding) models.

**Chunking**
Splitting long documents into 512-token pieces that fit within embedding model context windows.

**Upsert**
Insert-or-update. How we add doc chunks to the vector database — if a chunk already exists (same library + URL hash), update it; otherwise insert.

**Celery Beat**
Celery's periodic task scheduler. Used for daily re-indexing cron jobs.

**OCR (Optical Character Recognition)**
Converting scanned PDFs (images) to machine-readable text. We use Tesseract.

**Crawl Depth**
How many link-hops from the start URL the crawler follows. `crawl_depth: 3` means: start URL → link → link → link (3 levels deep).

---

## Business Terminology

**Free Tier**
100 queries/day, top 30 libraries, English only. No credit card required.

**Pro Tier**
₹399/month. Unlimited queries, all 100+ libraries, Hindi + regional, offline packs, private indexing.

**Team Tier**
₹999/seat/month. Pro + team management, unlimited private repos, SLA, analytics.

**Sponsored Library**
An API provider (Razorpay, Zerodha) pays ₹50K–2L/year to have their docs featured prominently and kept fresh daily. Separate from ad revenue (we don't do ads).

**Document-a-thon**
Community hackathon event where developers contribute new library configs to the index for cash prizes.

**iSPIRT**
Indian Software Product Industry Round Table. Non-profit that builds India Stack. Key community partner.

**FOSS United**
India's largest open-source community. Regional events in 10+ cities. Key launch partner.
