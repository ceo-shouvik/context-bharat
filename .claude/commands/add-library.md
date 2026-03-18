# /add-library

Add a new library to the Context7 India index.

## Steps Claude will take
1. Ask: library name, URL, category, languages needed
2. Create `backend/config/libraries/{slug}.json` from template
3. Add row to `knowledge-base/api-catalog.md`
4. Run `python scripts/ingest.py --library {slug} --dry-run` to preview
5. Ask to confirm and run full ingestion

## Config template
```json
{
  "library_id": "/{owner}/{repo}",
  "name": "...",
  "description": "...",
  "category": "indian-fintech|india-dpi|indian-trading|enterprise-india|indian-ai|global-framework|saas-cloud",
  "source": { "type": "web|github|pdf|multi", "url": "...", "crawl_depth": 3 },
  "refresh_interval_hours": 24,
  "languages": ["en"],
  "tags": []
}
```
