# /ingest

Run ingestion for a specific library or category.

## Usage
```
/ingest razorpay
/ingest --category indian-fintech
/ingest --all --force
```

## What this does
1. Loads library config from `backend/config/libraries/{library}.json`
2. Runs the ingestion pipeline (crawl → chunk → embed → upsert)
3. Reports chunks indexed and any errors

## Command to run
```bash
cd backend && python scripts/ingest.py --library {LIBRARY_NAME}
```
