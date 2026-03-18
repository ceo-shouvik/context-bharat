# Ingestion Pipeline

How documentation gets from source (GitHub, web, PDF, gov portal) into the vector database.

---

## Pipeline Overview

Every library ingestion runs through 7 stages:

```
Source → Crawl → Extract → Chunk → Enrich → Embed → Translate → Upsert
```

Triggered by:
- **Daily cron** (GitHub Actions, 2 AM IST) — re-index all libraries past their `refresh_interval_hours`
- **Version bump webhook** — GitHub webhook on release tags in tracked repos
- **Admin CLI** — `python scripts/ingest.py --library <id>`
- **PR merge** — when a new library config is merged to main

---

## Stage 1: Crawl

### Web Crawling (Crawl4AI)

Used for: Documentation websites (Razorpay docs, Cashfree Dev Studio, ONDC docs)

```python
from crawl4ai import AsyncWebCrawler

async def crawl_web(url: str, config: dict) -> list[RawDocument]:
    async with AsyncWebCrawler(
        headless=True,
        browser_type="chromium",   # Playwright-based, handles JS SPAs
        verbose=False,
    ) as crawler:
        result = await crawler.arun(
            url=url,
            word_count_threshold=50,           # Skip nav-only pages
            exclude_external_links=True,
            exclude_social_media_links=True,
            process_iframes=False,
            remove_overlay_elements=True,      # Cookie banners, modals
            css_selector="main, article, .docs-content",  # Focus on content
        )
        return [RawDocument(
            url=url,
            content=result.markdown,           # Crawl4AI outputs clean Markdown
            content_type="markdown",
            metadata={"title": result.metadata.get("title", "")}
        )]
```

**Depth crawling** — for full documentation sites:
```python
# Follows links up to crawl_depth levels
# Respects robots.txt by default
# Rate limiting: 1 req/sec for government sites, 5 req/sec for commercial
```

**Authenticated portals** (ABDM sandbox, some government portals):
```python
# Session-based auth — configure in library JSON:
# "auth": { "type": "form", "login_url": "...", "username_field": "...", "password_field": "..." }
# Credentials stored in environment variables, not in config JSON
```

### PDF Crawling

Used for: UPI/NPCI specs, GSTN PDFs, DigiLocker spec, older government docs

```python
import pdfplumber  # For text-based PDFs (tables, structured content)
import pytesseract  # For scanned image PDFs
from pdf2image import convert_from_path

def crawl_pdf(pdf_url: str) -> list[RawDocument]:
    # Download PDF
    pdf_path = download_to_temp(pdf_url)

    # Try text extraction first (faster, better quality)
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            # Extract text preserving reading order
            page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
            # Extract tables → Markdown format
            for table in page.extract_tables():
                page_text += table_to_markdown(table)
            text += page_text

    # If text extraction yields <100 words per page → it's a scanned PDF
    if words_per_page(text) < 100:
        text = ocr_pdf(pdf_path)  # Fall back to Tesseract OCR

    return [RawDocument(url=pdf_url, content=text, content_type="markdown")]

def ocr_pdf(pdf_path: str) -> str:
    """OCR a scanned PDF using Tesseract."""
    images = convert_from_path(pdf_path, dpi=300)
    text = ""
    for image in images:
        # lang='eng+hin' for Hindi PDFs
        page_text = pytesseract.image_to_string(image, lang='eng')
        text += page_text + "\n\n"
    return text
```

**OCR quality scoring:**
- Confidence threshold: 70% (below this → flag for human review queue)
- Store confidence score in chunk metadata
- Low-confidence chunks marked with warning in API response

### GitHub Crawling

Used for: ONDC repos, Frappe, open-source SDKs with docs in the repo

```python
import httpx

async def crawl_github(repo: str, config: dict) -> list[RawDocument]:
    # Use GitHub API to list files (avoids cloning)
    token = os.getenv("GITHUB_TOKEN")  # Higher rate limit with auth
    headers = {"Authorization": f"token {token}"}

    # Get default branch
    repo_info = await fetch(f"https://api.github.com/repos/{repo}", headers)
    default_branch = repo_info["default_branch"]

    # List files recursively
    tree = await fetch(
        f"https://api.github.com/repos/{repo}/git/trees/{default_branch}?recursive=1",
        headers
    )

    # Filter to doc files
    doc_files = [
        f for f in tree["tree"]
        if f["path"].endswith((".md", ".mdx", ".rst", ".txt"))
        and not any(skip in f["path"] for skip in ["node_modules", ".github", "test", "spec"])
    ]

    # Fetch file content (raw)
    docs = []
    for file in doc_files[:config.get("max_files", 200)]:
        raw_url = f"https://raw.githubusercontent.com/{repo}/{default_branch}/{file['path']}"
        content = await fetch_text(raw_url)
        docs.append(RawDocument(
            url=f"https://github.com/{repo}/blob/{default_branch}/{file['path']}",
            content=content,
            content_type="markdown",
        ))
    return docs
```

---

## Stage 2: Extract & Clean

Clean the raw crawled content before chunking.

```python
def clean_document(doc: RawDocument) -> RawDocument:
    content = doc.content

    # Remove repeated navigation text (appears on every page)
    content = remove_nav_patterns(content)

    # Preserve code blocks exactly — never clean inside ``` blocks
    code_blocks = extract_code_blocks(content)
    content_without_code = replace_code_blocks_with_placeholders(content)

    # Clean prose content
    content_without_code = remove_excessive_whitespace(content_without_code)
    content_without_code = remove_html_comments(content_without_code)
    content_without_code = normalize_headers(content_without_code)

    # Restore code blocks
    content = restore_code_blocks(content_without_code, code_blocks)

    return dataclasses.replace(doc, content=content)
```

---

## Stage 3: Chunk

Split cleaned documents into 512-token chunks.

```python
from llama_index.core.node_parser import SentenceSplitter

def chunk_document(doc: RawDocument) -> list[Chunk]:
    splitter = SentenceSplitter(
        chunk_size=512,       # tokens
        chunk_overlap=50,     # overlap for context continuity
        paragraph_separator="\n\n",
        secondary_chunking_regex="(?<=\n)",  # Respect line breaks
    )

    chunks = splitter.split_text(doc.content)

    return [
        Chunk(
            content=chunk,
            library_id=doc.library_id,
            url=doc.url,
            section=extract_section_heading(chunk),
            content_hash=sha256(chunk),
            language="en",  # Will be detected in Enrich stage
        )
        for chunk in chunks
    ]
```

**Section boundary respect:** Chunks never split in the middle of a code block. Section headers (`## API Reference`) always start a new chunk.

---

## Stage 4: Enrich

Add LLM-generated metadata to each chunk. Uses Claude Haiku (fast + cheap).

```python
async def enrich_chunk(chunk: Chunk) -> Chunk:
    prompt = f"""Analyze this documentation chunk and respond in JSON only:

{chunk.content[:1000]}

JSON response:
{{
  "chunk_type": "api_reference|guide|example|changelog|overview",
  "api_endpoint": "/endpoint/path or null",
  "language": "en|hi|ta|te|kn|bn",
  "has_code_example": true/false,
  "programming_languages": ["python", "javascript"],
  "complexity": "beginner|intermediate|advanced"
}}"""

    response = await claude_haiku(prompt)
    metadata = json.loads(response)

    return dataclasses.replace(chunk, metadata={**chunk.metadata, **metadata})
```

**Cost:** ~$0.001 per 1000 chunks (Claude Haiku pricing). 100K chunks = $0.10.

---

## Stage 5: Embed

Generate vector embeddings for each chunk.

```python
from openai import AsyncOpenAI

async def embed_chunks(chunks: list[Chunk]) -> list[Chunk]:
    client = AsyncOpenAI()

    # Process in batches of 100 (OpenAI batch limit)
    batches = [chunks[i:i+100] for i in range(0, len(chunks), 100)]
    all_embeddings = []

    for batch in batches:
        response = await client.embeddings.create(
            model="text-embedding-3-small",  # 1536 dims, $0.02/1M tokens
            input=[c.content for c in batch],
            encoding_format="float",
        )
        all_embeddings.extend([e.embedding for e in response.data])

    return [
        dataclasses.replace(chunk, embedding=embedding)
        for chunk, embedding in zip(chunks, all_embeddings)
    ]
```

---

## Stage 6: Translate (Optional)

For libraries with non-English language configs, generate translated versions.

```python
from sarvam_ai import SarvamClient

async def translate_chunk(chunk: Chunk, target_lang: str) -> Chunk:
    client = SarvamClient(api_key=os.getenv("SARVAM_API_KEY"))

    # Don't translate code blocks
    prose, code_blocks = separate_prose_and_code(chunk.content)

    translated_prose = await client.translate(
        text=prose,
        source_language="en",
        target_language=target_lang,  # "hi", "ta", "te", etc.
        domain="technical",           # Better handling of technical terms
    )

    # Restore code blocks untranslated
    translated_content = merge_prose_and_code(translated_prose, code_blocks)

    # Generate new embedding for translated content
    translated_embedding = await embed_single(translated_content)

    return Chunk(
        content=translated_content,
        library_id=chunk.library_id,
        url=chunk.url,
        section=chunk.section,
        language=target_lang,
        content_hash=sha256(translated_content),
        embedding=translated_embedding,
        metadata={**chunk.metadata, "translated_from": "en"},
    )
```

---

## Stage 7: Upsert

Insert or update chunks in the vector database.

```python
async def upsert_chunks(library_id: str, chunks: list[Chunk], session: AsyncSession):
    # Get existing chunk hashes for this library
    existing_hashes = await get_existing_hashes(library_id, session)
    this_run_hashes = set()

    for chunk in chunks:
        this_run_hashes.add(chunk.content_hash)

        if chunk.content_hash in existing_hashes:
            # Update metadata only (content unchanged)
            await update_chunk_metadata(chunk, session)
        else:
            # New chunk → insert
            await insert_chunk(chunk, session)

    # Delete chunks no longer present (page deleted or content significantly changed)
    stale_hashes = existing_hashes - this_run_hashes
    if stale_hashes:
        await delete_chunks_by_hash(library_id, stale_hashes, session)

    await session.commit()
```

---

## Error Handling & Retry

```python
from celery import Task
from tenacity import retry, stop_after_attempt, wait_exponential

class IngestionTask(Task):
    # Celery auto-retry on failure
    autoretry_for = (httpx.TimeoutException, RateLimitError)
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 min between retries
    max_retries = 3

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
)
async def fetch_with_retry(url: str) -> str:
    """Fetch a URL with exponential backoff retry."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
```

**Government portal specific handling:**
- Portal down: log + skip, retry next day
- Rate limited (429): respect Retry-After header
- Auth expired: alert via Slack, pause library until manually fixed
- PDF corrupt: log + skip chunk, store error in ingestion_runs

---

## Monitoring

```python
# Every ingestion run logged to ingestion_runs table
# Metrics tracked:
# - chunks_indexed: total chunks successfully upserted
# - chunks_deleted: stale chunks removed
# - errors: list of {url, error_type, message}
# - duration_seconds: total pipeline time
# - embedding_cost_usd: OpenAI embedding API cost for this run

# Alerts (Slack webhook):
# - Ingestion failure after 3 retries
# - Freshness score < 0.5 for high-priority libraries (Razorpay, Zerodha)
# - OCR confidence < 70% on government PDFs
```

---

## Testing Ingestion Locally

```bash
# Dry run — show what would be indexed without writing to DB
python scripts/ingest.py --library razorpay --dry-run

# Full run (writes to local Postgres)
python scripts/ingest.py --library razorpay

# Force re-index even if fresh
python scripts/ingest.py --library razorpay --force

# Test a search query after indexing
python scripts/test_query.py --library razorpay --query "create payment link" --lang en

# Run ingestion for a whole category
python scripts/ingest.py --category indian-fintech

# Translate a library to Hindi
python scripts/translate.py --library razorpay --lang hi
```
