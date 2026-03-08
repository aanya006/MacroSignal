---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - 'prd.md'
  - 'architecture.md'
  - 'ux-design-specification.md'
  - 'NFC Hackathon Seeding Round .pdf'
---

# FinTech_Hackathon - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for FinTech_Hackathon, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System can ingest news articles from multiple free-tier news APIs on a scheduled batch cycle
FR2: System can filter ingested articles by financial and macroeconomic keywords before processing
FR3: System can prioritize Singapore/Asia-focused news sources (MAS, CNA, Business Times, Reuters Asia)
FR4: System can store ingested articles with metadata (title, source, date, URL, full text) in the database
FR5: System can serve cached data when a news API source is unavailable
FR6: System can cluster ingested articles into recognizable macro themes (e.g. "Fed Policy", "MAS Monetary Policy", "China Manufacturing")
FR7: System can assign a Hot/Warm/Cool temperature score to each theme based on article count and recency
FR8: System can tag each theme with affected regions (US, EU, Asia/Singapore) and asset classes (Equities, Bonds, FX, Commodities)
FR9: System can track theme article dates within a rolling 30-day window to support interactive date-based timeline navigation
FR10: System can update theme scores and clustering on each ingestion cycle
FR11: System can generate a structured causal chain (Trigger → Mechanism → per-asset-class impacts for Equities, Bonds, FX, Commodities with directional indicators) for each hot theme using Claude API
FR12: System can cache generated causal chains to avoid redundant API calls for the same theme within a time window
FR13: System can display causal chains in plain language accessible to non-quantitative users
FR14: System can label all AI-generated causal chains with an "AI-generated — not financial advice" disclaimer
FR15: System can store all detected themes and their associated articles as historical records
FR16: Asset manager can search historical themes by keyword (e.g. "MAS tightening", "inflation 2024")
FR17: System can surface historical theme context when a similar pattern recurs (e.g. "this theme appeared before — here's what happened")
FR18: System can display pre-seeded historical data to demonstrate institutional memory at launch
FR19: Asset manager can view a theme feed ranked by hot/cool score as the primary dashboard view
FR20: Asset manager can click on a theme to view its detail page with articles, timeline, causal chain, and tags
FR21: Asset manager can view article cards showing title, source name, date, and one-line AI summary for each article in a theme
FR22: Asset manager can click an article card to navigate to the original source article
FR23: Asset manager can navigate an interactive date timeline (last 30 days only) to filter articles by date, with fast-scroll animation on date selection and most recent articles shown by default
FR24: Asset manager can search and filter themes by keyword from the dashboard
FR25: Asset manager can view cross-region and cross-asset tags on each theme as color-coded badges
FR26: System can generate a one-line AI summary for each ingested article
FR27: System can attribute each article to its original source in compliance with API terms of service
FR28: System can display article publication date and source name alongside each article card
FR29: System can run news ingestion on an automated schedule (every 30 minutes)
FR30: System can handle API rate limits gracefully without crashing or losing data
FR31: System can serve the dashboard from pre-processed cached data for fast load times
FR32: System can tag articles with affected regions and asset classes using keyword-based classification during ingestion, with a predefined keyword map covering Singapore, US, China, ASEAN, EU, Japan regions and Equities, Bonds, FX, Commodities asset classes

### NonFunctional Requirements

NFR1: Dashboard initial load completes within 3 seconds serving pre-cached theme data
NFR2: Theme detail view (click to expand) renders within 1 second
NFR3: Causal chain panel displays within 2 seconds (served from Redis cache, not generated on-demand)
NFR4: Theme search/filter returns results within 500ms (client-side filtering on loaded data)
NFR5: News ingestion batch cycle completes within 60 seconds per run
NFR6: All API keys (news APIs, Claude API) stored as environment variables, never committed to repository
NFR7: Backend API does not expose raw API keys or internal system details to the frontend
NFR8: No user authentication required for the hackathon prototype — open access
NFR9: System gracefully handles news API failures — dashboard continues to serve cached data with "last updated" timestamp
NFR10: System respects news API rate limits — batch scheduling prevents exceeding free-tier quotas
NFR11: Claude API calls include timeout handling — dashboard renders without causal chains if Claude is unavailable
NFR12: All external API dependencies have fallback behavior — no single API failure crashes the application
NFR13: Theme clustering produces at minimum 5 and at most 15 distinct themes per ingestion cycle
NFR14: AI-generated article summaries limited to one sentence (max 30 words) for scannability
NFR15: Causal chains follow consistent Trigger → Mechanism → per-asset-class impacts (Equities, Bonds, FX, Commodities) format across all themes

### Additional Requirements

**From Architecture:**
- Starter template: Vite + React frontend, Flask backend — project initialization is first implementation task
- Database: PostgreSQL with raw SQL via psycopg2-binary, schema managed via schema.sql
- Cache: Redis for all hot data (themes TTL 5min, causal chains TTL 2h, summaries TTL 24h, API responses TTL 30min)
- API contract defined: 6 REST endpoints (GET /api/themes, /api/themes/:slug, /api/themes/:slug/articles?date=, /api/articles, /api/memory/search, /api/status)
- Response envelope: all responses wrapped in {"data": ..., "meta": {"last_updated": "ISO timestamp"}}
- Frontend state: Zustand store for theme data, selected theme, search state
- Routing: React Router with 2 routes (/ and /theme/:slug)
- Scheduling: APScheduler in Flask process for 30-min ingestion cycles
- CORS: flask-cors configured for localhost:5173
- Environment: .env file with python-dotenv, .gitignore for .env/venv/node_modules

**From UX Design:**
- Dark terminal aesthetic: background #0f172a, surfaces #1e293b, temperature colors (Hot red, Warm amber, Cool cyan)
- Compact feed panel (320px) with minimal cards: theme name, temperature badge, article count, recency
- Detail panel: theme banner with darkened background image, tags row, two-column layout (articles left, causal chain right)
- Custom components: ThemeFeedCard, ThemeBanner, RegionsMarketsBox, CausalChain (vertical step flow with gradient arrows + 2x2 per-asset-class impact grid), HistoricalParallel (purple-accented distinct section), ArticleHero, ArticleCard, DateTimeline (interactive date navigation with fast-scroll article filtering), StatusBar
- Tailwind CSS + shadcn/ui (copy-paste model)
- No emojis — all plain text labels
- Progressive disclosure pattern: feed → detail panel → historical parallels
- Two tabs: "Live Themes" (default) and "Memory Search"
- Auto-expand hottest theme on load
- Keyboard navigation: Tab/Arrow keys through feed, Enter to select
- Semantic HTML: nav, main, article, ol elements

**From Hackathon Requirements (PDF):**
- Deliverables: public GitHub repo, project description (200 words), 5-min YouTube video pitch
- Submission deadline: 11 Mar 9am
- Must address all expected features: topic evolution tracking, hot/cool detection, cross-region connections, institutional memory, intuitive dashboard
- Bonus: risk implications (causal chain reasoning)
- Judging: Innovation 20%, Technology/Prototype 20%, UX 20%, Feasibility/Impact 20%, Market Potential 20%

### FR Coverage Map

FR1: Epic 1 - Ingest news from multiple APIs
FR2: Epic 1 - Filter by financial keywords
FR3: Epic 1 - Prioritize SG/Asia sources
FR4: Epic 1 - Store articles with metadata
FR5: Epic 1 - Serve cached data on API failure
FR6: Epic 1 - Cluster articles into themes
FR7: Epic 1 - Temperature scoring (Hot/Warm/Cool)
FR8: Epic 2 - Tag themes with regions & asset classes
FR9: Epic 2 - Track theme dates for timeline
FR10: Epic 1 - Update theme scores each cycle
FR11: Epic 3 - Generate causal chains via Claude API
FR12: Epic 3 - Cache causal chains
FR13: Epic 3 - Display chains in plain language
FR14: Epic 3 - AI-generated disclaimer labels
FR15: Epic 4 - Store themes as historical records
FR16: Epic 4 - Search historical themes by keyword
FR17: Epic 4 - Surface recurring pattern context
FR18: Epic 4 - Pre-seeded historical data
FR19: Epic 1 - Theme feed ranked by temperature
FR20: Epic 2 - Theme detail page
FR21: Epic 2 - Article cards with summary
FR22: Epic 2 - Click-through to original source
FR23: Epic 2 - Interactive date timeline
FR24: Epic 1 - Search/filter themes by keyword
FR25: Epic 2 - Cross-region/asset badges
FR26: Epic 2 - One-line AI article summaries
FR27: Epic 2 - Source attribution
FR28: Epic 2 - Display date & source on cards
FR29: Epic 1 - Automated 30-min ingestion schedule
FR30: Epic 1 - Graceful rate limit handling
FR31: Epic 1 - Fast dashboard from cached data
FR32: Epic 2 - Keyword-based region/asset classification

## Epic List

### Epic 1: Live News Theme Dashboard
Asset managers can view a real-time feed of macro themes (e.g., "Fed Policy", "MAS Monetary Policy") ranked by temperature (Hot/Warm/Cool), search and filter themes, and see the dashboard load fast from cached data. Includes the full news ingestion pipeline, theme clustering, temperature scoring, scheduled updates, and the main dashboard UI.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR10, FR19, FR24, FR29, FR30, FR31

### Epic 2: Theme Deep Dive & Article Exploration
Asset managers can click a theme to explore its articles with one-line AI summaries, navigate an interactive date timeline, see cross-region and cross-asset-class tags as color-coded badges, and click through to original sources with proper attribution.
**FRs covered:** FR8, FR9, FR20, FR21, FR22, FR23, FR25, FR26, FR27, FR28, FR32

### Epic 3: AI-Powered Causal Chain Analysis
Asset managers can view AI-generated causal chains (Trigger → Mechanism → per-asset-class impacts for Equities, Bonds, FX, Commodities) for hot themes, helping them understand how macro events ripple across asset classes. Chains are cached, displayed in plain language, and labeled with disclaimers.
**FRs covered:** FR11, FR12, FR13, FR14

### Epic 4: Institutional Memory & Historical Context
Asset managers can search historical themes by keyword and see when similar patterns have occurred before. The system surfaces historical parallels when recurring patterns are detected and displays pre-seeded historical data to demonstrate institutional memory at launch.
**FRs covered:** FR15, FR16, FR17, FR18

---

## Epic 1: Live News Theme Dashboard

Asset managers can view a real-time feed of macro themes ranked by temperature (Hot/Warm/Cool), search and filter themes, and see the dashboard load fast from cached data. Includes the full news ingestion pipeline, theme clustering, temperature scoring, scheduled updates, and the main dashboard UI.

### Story 1.1: Project Initialization & Backend Foundation

As a developer,
I want a fully initialized project with Vite+React frontend, Flask backend, PostgreSQL database, and Redis cache,
So that all subsequent stories have a working foundation to build on.

**Acceptance Criteria:**

**Given** the project repository is cloned
**When** the developer runs the setup commands
**Then** a Vite + React frontend starts on localhost:5173 with Tailwind CSS and shadcn/ui configured
**And** a Flask backend starts on localhost:5000 with flask-cors configured for localhost:5173
**And** PostgreSQL is connected via psycopg2-binary with a schema.sql creating articles and themes tables
**And** Redis is connected and accessible for caching
**And** a .env file exists with placeholders for NEWS_API_KEY, CLAUDE_API_KEY, DATABASE_URL, REDIS_URL
**And** .gitignore excludes .env, venv/, node_modules/
**And** GET /api/status returns {"data": {"status": "ok"}, "meta": {"last_updated": "<ISO timestamp>"}}
**And** the response envelope pattern {"data": ..., "meta": {"last_updated": ...}} is established as a reusable pattern

### Story 1.2: News Ingestion Pipeline

As a system,
I want to ingest news articles from multiple free-tier APIs, filter them by financial keywords, and store them with metadata,
So that the platform has a continuous supply of relevant macro news to analyze.

**Acceptance Criteria:**

**Given** the ingestion pipeline is triggered (manually or by schedule)
**When** the system fetches articles from configured news APIs (e.g., NewsAPI, GNews)
**Then** articles are filtered by a predefined list of financial and macroeconomic keywords (e.g., "inflation", "interest rate", "GDP", "central bank", "tariff")
**And** Singapore/Asia-focused sources (MAS, CNA, Business Times, Reuters Asia) are prioritized in the query parameters
**And** each article is stored in PostgreSQL with title, source name, publication date, URL, and full text
**And** duplicate articles (same URL) are skipped without error
**And** if a news API returns a rate limit error (HTTP 429), the system logs the error and continues with other sources without crashing
**And** if a news API is completely unavailable, the system logs the failure and proceeds with remaining sources
**And** the ingestion batch completes within 60 seconds per run (NFR5)
**And** API keys are read from environment variables, never hardcoded (NFR6)

### Story 1.3: Theme Clustering & Temperature Scoring

As a system,
I want to cluster ingested articles into recognizable macro themes and assign temperature scores,
So that asset managers can quickly see which macro topics are most active.

**Acceptance Criteria:**

**Given** articles exist in the database from the ingestion pipeline
**When** the clustering process runs
**Then** articles are grouped into recognizable macro themes (e.g., "Fed Policy", "MAS Monetary Policy", "China Manufacturing") using keyword-based clustering
**And** each theme is assigned a slug (URL-safe identifier), display name, and description
**And** each theme receives a temperature score of Hot, Warm, or Cool based on article count and recency (articles in last 24h weighted higher)
**And** the clustering produces between 5 and 15 distinct themes (NFR13)
**And** theme scores and cluster assignments are updated on each ingestion cycle
**And** themes and their article associations are stored in PostgreSQL
**And** theme data is cached in Redis with a 5-minute TTL

### Story 1.4: Theme Feed API & Scheduled Ingestion

As a system,
I want to expose theme data via a REST API and run ingestion on an automated schedule,
So that the frontend can display up-to-date theme data and the pipeline runs without manual intervention.

**Acceptance Criteria:**

**Given** themes exist in the database and Redis cache
**When** the frontend calls GET /api/themes
**Then** the API returns all themes ranked by temperature (Hot first, then Warm, then Cool) in the standard response envelope
**And** each theme object includes: slug, name, temperature, article_count, latest_article_date, description
**And** the response is served from Redis cache for fast load times (NFR1: under 3 seconds)
**And** if Redis cache is empty or expired, the API falls back to PostgreSQL and repopulates the cache
**And** APScheduler runs the full ingestion + clustering pipeline every 30 minutes
**And** the GET /api/status endpoint includes a "last_updated" timestamp reflecting the most recent successful ingestion
**And** if all news APIs are unavailable during a cycle, the dashboard continues serving previously cached data (NFR9)

### Story 1.5: Dashboard Theme Feed UI

As an asset manager,
I want to view a theme feed ranked by temperature on a dark terminal-aesthetic dashboard,
So that I can quickly identify which macro themes demand my attention.

**Acceptance Criteria:**

**Given** the dashboard is loaded at the root route (/)
**When** theme data is fetched from GET /api/themes
**Then** a compact feed panel (320px width) displays ThemeFeedCard components for each theme
**And** each card shows: theme name, temperature badge (Hot=red, Warm=amber, Cool=cyan), article count, and recency indicator
**And** themes are ranked by temperature score (Hot first)
**And** the hottest theme is auto-expanded/selected on initial load
**And** the dashboard uses the dark terminal aesthetic (background #0f172a, surfaces #1e293b)
**And** a search input allows filtering themes by keyword with results appearing within 500ms (NFR4, client-side filtering)
**And** two tabs are visible: "Live Themes" (default active) and "Memory Search"
**And** keyboard navigation works: Tab/Arrow keys move through feed, Enter selects a theme
**And** a StatusBar component shows the last_updated timestamp from the API
**And** semantic HTML is used (nav, main, article elements)
**And** no emojis appear in any labels — all plain text
**And** Zustand store manages theme data and selected theme state

---

## Epic 2: Theme Deep Dive & Article Exploration

Asset managers can click a theme to explore its articles with one-line AI summaries, navigate an interactive date timeline, see cross-region and cross-asset-class tags as color-coded badges, and click through to original sources with proper attribution.

### Story 2.1: Region & Asset Class Tagging During Ingestion

As a system,
I want to tag each article with affected regions and asset classes during ingestion using keyword-based classification,
So that themes can display cross-region and cross-asset intelligence.

**Acceptance Criteria:**

**Given** an article is being processed during ingestion
**When** the keyword classifier runs on the article text
**Then** the article is tagged with zero or more regions from: Singapore, US, China, ASEAN, EU, Japan using a predefined keyword map
**And** the article is tagged with zero or more asset classes from: Equities, Bonds, FX, Commodities using a predefined keyword map
**And** region and asset class tags are stored in the database alongside the article
**And** theme-level tags are aggregated from their constituent articles (a theme is tagged with a region/asset if multiple articles carry that tag)
**And** the predefined keyword map is configurable (stored as a Python dict or JSON file)

### Story 2.2: Theme Detail API & Article Retrieval

As a system,
I want to expose theme detail and article data via REST endpoints,
So that the frontend can render the full theme detail view.

**Acceptance Criteria:**

**Given** a theme exists with associated articles
**When** the frontend calls GET /api/themes/:slug
**Then** the API returns the theme with: name, slug, temperature, description, regions array, asset_classes array, article_count, date_range
**And** the response follows the standard envelope format
**When** the frontend calls GET /api/themes/:slug/articles (optionally with ?date= parameter)
**Then** the API returns articles for that theme, ordered by publication date (most recent first)
**And** each article includes: title, source_name, publication_date, url, ai_summary, regions, asset_classes
**And** if a date parameter is provided, only articles from that date are returned
**And** article dates within a rolling 30-day window are tracked to support timeline navigation
**And** the theme detail response renders within 1 second (NFR2)

### Story 2.3: AI Article Summaries

As a system,
I want to generate a one-line AI summary for each ingested article,
So that asset managers can quickly scan article relevance without reading full text.

**Acceptance Criteria:**

**Given** an article has been ingested and stored
**When** the summary generation process runs
**Then** each article receives a one-line AI summary generated via Claude API
**And** each summary is limited to one sentence, maximum 30 words (NFR14)
**And** summaries are cached in Redis with a 24-hour TTL
**And** if Claude API is unavailable or times out, the article is stored without a summary (no crash)
**And** articles without summaries display the first 30 words of the article text as a fallback
**And** summary generation respects API rate limits

### Story 2.4: Theme Detail View UI

As an asset manager,
I want to click a theme and see its full detail view with articles, tags, and timeline,
So that I can explore a macro theme in depth.

**Acceptance Criteria:**

**Given** the asset manager clicks a theme in the feed panel or navigates to /theme/:slug
**When** the detail view loads
**Then** a ThemeBanner displays at the top with the theme name and darkened background
**And** a tags row shows RegionsMarketsBox with cross-region and cross-asset badges as color-coded pills
**And** the detail panel uses a two-column layout (articles left, causal chain right — causal chain placeholder for now)
**And** an ArticleHero component highlights the most recent article with title, source, date, and AI summary
**And** ArticleCard components list remaining articles with: title, source name, publication date, and one-line AI summary
**And** each article card is clickable and navigates to the original source URL in a new tab
**And** source attribution (source name + date) is displayed on every article card (FR27, FR28)
**And** React Router handles the /theme/:slug route
**And** the view renders within 1 second (NFR2)

### Story 2.5: Interactive Date Timeline

As an asset manager,
I want to navigate an interactive date timeline to filter articles by date,
So that I can track how a theme evolved over time.

**Acceptance Criteria:**

**Given** the theme detail view is loaded with articles spanning multiple dates
**When** the DateTimeline component renders
**Then** it displays clickable date markers for each day that has articles (within a 30-day rolling window)
**And** the most recent date is selected by default, showing its articles
**And** clicking a date marker filters the article list to show only articles from that date
**And** a fast-scroll animation plays when navigating between dates
**And** the timeline is horizontally scrollable if dates exceed the visible area
**And** the article list updates immediately on date selection (client-side filtering)
**And** the date timeline shows visual density indicators (more articles = more prominent marker)

---

## Epic 3: AI-Powered Causal Chain Analysis

Asset managers can view AI-generated causal chains (Trigger → Mechanism → per-asset-class impacts for Equities, Bonds, FX, Commodities) for hot themes, helping them understand how macro events ripple across asset classes.

### Story 3.1: Causal Chain Generation via Claude API

As a system,
I want to generate structured causal chains for hot themes using Claude API,
So that asset managers can understand how macro events impact different asset classes.

**Acceptance Criteria:**

**Given** a theme with temperature "Hot" exists with associated articles
**When** the causal chain generation process runs
**Then** the system calls Claude API with the theme name, description, and recent article summaries as context
**And** the response is parsed into a structured causal chain with: Trigger (the macro event), Mechanism (how it transmits through markets), and per-asset-class impacts for Equities, Bonds, FX, and Commodities each with a directional indicator (positive/negative/neutral)
**And** the causal chain is written in plain language accessible to non-quantitative users (FR13)
**And** the generated chain is cached in Redis with a 2-hour TTL (NFR3)
**And** if Claude API is unavailable or times out, the system logs the error and the theme displays without a causal chain (NFR11)
**And** the causal chain follows the consistent format: Trigger → Mechanism → per-asset-class impacts (NFR15)

### Story 3.2: Causal Chain Display UI

As an asset manager,
I want to view the causal chain for a theme in the detail panel,
So that I can understand the market implications of a macro event at a glance.

**Acceptance Criteria:**

**Given** a theme detail view is open and a causal chain exists for that theme
**When** the CausalChain component renders in the right column of the detail panel
**Then** it displays a vertical step flow with gradient arrows showing: Trigger → Mechanism → Asset Impacts
**And** the asset impacts section shows a 2x2 grid with Equities, Bonds, FX, Commodities each with a directional indicator
**And** all text is plain language, no jargon or formulas
**And** an "AI-generated — not financial advice" disclaimer label is displayed at the bottom of the causal chain (FR14)
**And** the causal chain panel displays within 2 seconds (NFR3, served from Redis cache)
**And** if no causal chain is available (API failure or non-hot theme), the right column shows a "Causal analysis not yet available" placeholder
**And** no emojis are used in any labels

---

## Epic 4: Institutional Memory & Historical Context

Asset managers can search historical themes by keyword and see when similar patterns have occurred before. The system surfaces historical parallels when recurring patterns are detected and displays pre-seeded historical data to demonstrate institutional memory at launch.

### Story 4.1: Historical Theme Storage & Pre-Seeded Data

As a system,
I want to store all detected themes as historical records and load pre-seeded historical data,
So that the platform has institutional memory from day one.

**Acceptance Criteria:**

**Given** themes are detected during each ingestion cycle
**When** the clustering process completes
**Then** all themes and their associated articles are stored as historical records in PostgreSQL with timestamps
**And** historical records are never deleted — they accumulate over time
**And** a pre-seeded dataset of historical themes is loaded into the database on first run (e.g., past macro events like "2024 Fed Rate Decisions", "MAS Oct 2024 Policy", "China Property Crisis")
**And** pre-seeded themes include realistic article metadata, temperature scores, and region/asset tags
**And** the pre-seeded data is sufficient to demonstrate institutional memory during the hackathon demo (FR18)
**And** at minimum 5 historical themes are pre-seeded with 3+ articles each

### Story 4.2: Historical Theme Search API

As a system,
I want to expose a search endpoint for historical themes,
So that the frontend can power the Memory Search tab.

**Acceptance Criteria:**

**Given** historical themes exist in the database
**When** the frontend calls GET /api/memory/search?q=<keyword>
**Then** the API returns historical themes matching the keyword search (searching theme names, descriptions, and article titles)
**And** results are ordered by relevance (keyword match strength) then by date (most recent first)
**And** each result includes: theme name, date range, temperature at peak, article count, and a brief summary
**And** the response follows the standard envelope format
**And** if no results match, the API returns an empty data array (not an error)

### Story 4.3: Memory Search UI & Historical Parallels

As an asset manager,
I want to search historical themes and see when similar patterns occurred before,
So that I can leverage institutional memory to inform current decisions.

**Acceptance Criteria:**

**Given** the asset manager clicks the "Memory Search" tab on the dashboard
**When** the Memory Search view renders
**Then** a search input is displayed for keyword queries (e.g., "MAS tightening", "inflation 2024")
**And** search results show historical theme cards with: theme name, date range, peak temperature, article count
**And** clicking a historical theme shows its detail view with articles and context
**When** a current live theme has a historical parallel detected by the system
**Then** a HistoricalParallel component appears in the theme detail view with a purple-accented distinct section
**And** the parallel shows: "This theme appeared before — here's what happened" with a link to the historical theme
**And** the historical parallel matching uses keyword overlap between current and past theme names/articles (FR17)
**And** the Memory Search tab is accessible via keyboard navigation
