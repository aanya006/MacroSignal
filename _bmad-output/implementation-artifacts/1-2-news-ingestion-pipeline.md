# Story 1.2: News Ingestion Pipeline

Status: ready-for-dev

## Story

As a system,
I want to ingest news articles from multiple free-tier APIs, filter them by financial keywords, and store them with metadata,
so that the platform has a continuous supply of relevant macro news to analyze.

## Acceptance Criteria

1. **Given** the ingestion pipeline is triggered **When** the system fetches articles from configured news APIs **Then** articles are returned from at least one source (NewsAPI, GNews, or Google News RSS)
2. **Given** raw articles are fetched **When** the keyword filter runs **Then** only articles containing financial/macroeconomic keywords pass through (e.g., "inflation", "interest rate", "GDP", "central bank", "tariff", "monetary policy", "MAS", "Fed")
3. **Given** the keyword filter is applied **When** configuring source priority **Then** Singapore/Asia-focused sources (MAS, CNA, Business Times, Reuters Asia) are prioritized in query parameters
4. **Given** filtered articles are ready **When** they are stored **Then** each article has: title, source_name, url, published_at, full_text, ingested_at in the articles table
5. **Given** an article URL already exists in the database **When** the same article is ingested again **Then** it is skipped without error (deduplicated by URL unique constraint)
6. **Given** a news API returns HTTP 429 (rate limit) **When** the ingestion runs **Then** the system logs the error and continues with other sources without crashing
7. **Given** a news API is completely unavailable **When** the ingestion runs **Then** the system logs the failure and proceeds with remaining sources
8. **Given** the ingestion completes **When** checking the ingestion_logs table **Then** a new row exists with: articles_fetched, articles_new, status, run_at
9. **Given** all configuration **When** checking API keys **Then** they are read from environment variables via python-dotenv, never hardcoded

## Tasks / Subtasks

- [ ] Task 1: Define Financial Keyword List (AC: #2, #3)
  - [ ] Create backend/app/services/news_ingestion.py
  - [ ] Define FINANCIAL_KEYWORDS list: ["inflation", "interest rate", "GDP", "central bank", "monetary policy", "tariff", "trade war", "recession", "bond yield", "currency", "forex", "equity", "commodity", "oil price", "fed", "MAS", "ECB", "BOJ", "fiscal policy", "debt", "deficit", "employment", "PMI", "CPI", "manufacturing"]
  - [ ] Define PRIORITY_SOURCES list: ["CNA", "Business Times", "Reuters", "Straits Times", "MAS", "Bloomberg Asia"]
  - [ ] Define keyword filter function that checks article title + description against keyword list
- [ ] Task 2: NewsAPI Integration (AC: #1, #3, #6, #9)
  - [ ] Implement fetch_from_newsapi() function
  - [ ] Query parameters: q="macroeconomic OR monetary policy OR central bank", language=en, sortBy=publishedAt
  - [ ] Include Asia-focused domains in the query when possible
  - [ ] Handle HTTP 429 with try/except — log and return empty list
  - [ ] Handle connection errors — log and return empty list
  - [ ] Parse response into standardized article dicts: {title, source_name, url, published_at, full_text}
- [ ] Task 3: Secondary News Source (AC: #1, #7)
  - [ ] Implement fetch_from_gnews() or fetch_from_google_rss() as backup source
  - [ ] Same standardized output format as NewsAPI
  - [ ] Independent error handling — failure doesn't affect other sources
- [ ] Task 4: Article Storage (AC: #4, #5)
  - [ ] Implement store_articles(articles) function in news_ingestion.py
  - [ ] Use INSERT ... ON CONFLICT (url) DO NOTHING for deduplication
  - [ ] Track counts: total fetched vs. actually inserted (new)
  - [ ] Use db.py connection pool for database operations
- [ ] Task 5: Ingestion Orchestrator (AC: #6, #7, #8)
  - [ ] Implement run_ingestion() function that:
    1. Calls all news source fetchers
    2. Combines results
    3. Applies keyword filter
    4. Stores filtered articles
    5. Logs results to ingestion_logs table
  - [ ] Each source wrapped in try/except — never let one source crash the pipeline
  - [ ] Return summary: {articles_fetched, articles_new, sources_used, errors}
- [ ] Task 6: Manual Trigger Endpoint (for testing)
  - [ ] Create routes/ingestion.py with POST /api/ingest (dev-only endpoint)
  - [ ] Calls run_ingestion() and returns summary
  - [ ] Register blueprint in app factory

## Dev Notes

### Architecture Compliance

- **File location:** backend/app/services/news_ingestion.py
- **Database access:** Via models/db.py only — use the connection pool established in Story 1.1
- **Error handling:** try/except on EVERY external API call. Log error, return empty list, continue.
- **Response envelope:** Any API endpoints must use {"data": ..., "meta": {"last_updated": ...}}
- **Naming:** snake_case for all functions, variables, JSON fields

### NewsAPI Free Tier Constraints

- **100 requests/day** — must be conservative
- **Base URL:** https://newsapi.org/v2/everything
- **Required header:** X-Api-Key: {NEWS_API_KEY}
- **Useful params:** q (query), language, sortBy, from (date), pageSize (max 100)
- **Rate limit response:** HTTP 429

### GNews Free Tier (Alternative)

- **Base URL:** https://gnews.io/api/v4/search
- **100 requests/day** on free tier
- **Params:** q, lang=en, max=10, apikey

### Google News RSS (No API Key Needed)

- **URL pattern:** https://news.google.com/rss/search?q={query}&hl=en-SG&gl=SG
- **No rate limit** — but less structured data
- **Parse with:** xml.etree.ElementTree or feedparser library
- **Note:** feedparser not in requirements.txt — use xml.etree.ElementTree instead, or add feedparser

### SQL Patterns

```python
# Insert with deduplication
INSERT INTO articles (title, source_name, url, published_at, full_text, ingested_at)
VALUES (%s, %s, %s, %s, %s, NOW())
ON CONFLICT (url) DO NOTHING

# Log ingestion run
INSERT INTO ingestion_logs (articles_fetched, articles_new, themes_updated, status)
VALUES (%s, %s, 0, %s)
```

### Previous Story Dependencies

- Story 1.1 must be complete: PostgreSQL schema, Redis connection, Flask app factory, .env config
- Uses: models/db.py for database, utils/config.py for env vars

### Critical Warnings

- **DO NOT** call Claude API in this story — that's for Stories 2.3 and 3.1
- **DO NOT** do theme clustering here — that's Story 1.3
- **DO NOT** generate article summaries — that's Story 2.3
- **DO NOT** set region_tags or asset_tags on articles — that's Story 2.1
- **DO NOT** exceed free-tier rate limits — be conservative with API calls
- **DO NOT** store API keys in code — read from os.environ / python-dotenv

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Integration-Points]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.2]
- [Source: _bmad-output/planning-artifacts/prd.md#FR1-FR5]

## Dev Agent Record

### Agent Model Used



### Debug Log References

### Completion Notes List

### File List


