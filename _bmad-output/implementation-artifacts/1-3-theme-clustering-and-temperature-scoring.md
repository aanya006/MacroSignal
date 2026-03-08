# Story 1.3: Theme Clustering & Temperature Scoring

Status: ready-for-dev

## Story

As a system,
I want to cluster ingested articles into recognizable macro themes and assign temperature scores,
so that asset managers can quickly see which macro topics are most active.

## Acceptance Criteria

1. **Given** articles exist in the database **When** the clustering process runs **Then** articles are grouped into recognizable macro themes (e.g., "Fed Policy", "MAS Monetary Policy", "China Manufacturing")
2. **Given** themes are created **When** each theme is stored **Then** it has: name, slug (URL-safe), description, score_label, score_value, article_count, first_seen_at, last_updated_at
3. **Given** a theme exists **When** temperature scoring runs **Then** it receives Hot, Warm, or Cool based on article count and recency (articles in last 24h weighted higher)
4. **Given** the clustering completes **When** checking the themes table **Then** between 5 and 15 distinct themes exist
5. **Given** clustering runs on a subsequent ingestion cycle **When** new articles arrive **Then** existing themes are updated (not duplicated) and new themes are created if needed
6. **Given** themes are stored **When** checking the database **Then** each theme has a unique slug derived from its name
7. **Given** themes are scored **When** checking Redis cache **Then** theme data is cached with a 5-minute TTL under key `macro:themes:all`

## Tasks / Subtasks

- [ ] Task 1: Define Theme Configuration (AC: #1, #4)
  - [ ] Create backend/app/services/theme_clustering.py
  - [ ] Define THEME_DEFINITIONS — a predefined map of theme keywords to theme names:
    ```python
    THEME_DEFINITIONS = {
        "fed-policy": {"name": "Fed Policy Trajectory", "keywords": ["federal reserve", "fed", "fomc", "powell", "us interest rate", "fed funds"]},
        "mas-policy": {"name": "MAS Monetary Policy", "keywords": ["mas", "monetary authority", "singapore dollar", "sgd", "neer", "s$neer"]},
        "china-economy": {"name": "China Economic Outlook", "keywords": ["china gdp", "china manufacturing", "pmi china", "chinese economy", "yuan", "pboc"]},
        "us-inflation": {"name": "US Inflation & CPI", "keywords": ["us inflation", "cpi", "consumer price", "pce", "us prices"]},
        "global-trade": {"name": "Global Trade & Tariffs", "keywords": ["tariff", "trade war", "trade deal", "wto", "export", "import duties"]},
        "oil-energy": {"name": "Oil & Energy Markets", "keywords": ["oil price", "crude", "opec", "brent", "energy", "natural gas"]},
        "ecb-europe": {"name": "ECB & European Economy", "keywords": ["ecb", "european central bank", "eurozone", "eu economy", "euro"]},
        "boj-japan": {"name": "BOJ & Japan Economy", "keywords": ["boj", "bank of japan", "yen", "japan economy", "yield curve control"]},
        "emerging-markets": {"name": "Emerging Markets", "keywords": ["emerging market", "asean", "developing economies", "em bonds", "em currencies"]},
        "crypto-digital": {"name": "Crypto & Digital Assets", "keywords": ["bitcoin", "crypto", "blockchain", "digital currency", "cbdc"]},
        "tech-sector": {"name": "Technology Sector", "keywords": ["tech stocks", "semiconductor", "ai stocks", "nasdaq", "big tech"]},
        "geopolitical": {"name": "Geopolitical Risk", "keywords": ["geopolitical", "sanctions", "conflict", "war", "military", "geopolitics"]},
        "bonds-rates": {"name": "Bond Markets & Yields", "keywords": ["bond yield", "treasury", "sovereign debt", "yield curve", "bond market"]},
        "fx-currency": {"name": "FX & Currency Markets", "keywords": ["forex", "currency", "exchange rate", "dollar index", "dxy"]},
        "commodities": {"name": "Commodities & Metals", "keywords": ["gold", "silver", "copper", "commodity", "metals", "agriculture"]},
    }
    ```
  - [ ] This keyword-matching approach is intentionally simple for the hackathon — no ML/NLP needed
- [ ] Task 2: Article-to-Theme Matching (AC: #1, #5)
  - [ ] Implement classify_article(article) → list of matching theme slugs
  - [ ] Match article title + full_text against theme keywords (case-insensitive)
  - [ ] An article can match multiple themes
  - [ ] If article matches no themes, assign to a "General Macro" catch-all theme
  - [ ] Implement cluster_articles() that:
    1. Fetches unclassified articles (theme_id IS NULL) from database
    2. Classifies each article
    3. Updates article.theme_id for each match (use primary/best match for FK)
- [ ] Task 3: Theme Creation & Update (AC: #2, #5, #6)
  - [ ] Implement create_or_update_themes() function
  - [ ] For each theme in THEME_DEFINITIONS that has matching articles:
    - If theme slug doesn't exist in DB → INSERT new theme
    - If theme slug exists → UPDATE article_count, last_updated_at
  - [ ] Generate slug from theme name: lowercase, replace spaces with hyphens, strip special chars
  - [ ] Set description from THEME_DEFINITIONS or auto-generate from first article title
- [ ] Task 4: Temperature Scoring (AC: #3)
  - [ ] Implement calculate_temperature(theme_id) → (score_label, score_value)
  - [ ] Scoring formula:
    ```
    score_value = (articles_last_24h * 3) + (articles_last_72h * 1.5) + (articles_older * 0.5)
    ```
  - [ ] Label mapping:
    - score_value >= 10 → "hot"
    - score_value >= 4 → "warm"
    - score_value < 4 → "cool"
  - [ ] Update themes table with score_label and score_value
  - [ ] Thresholds are adjustable — tuned after seeing real data volumes
- [ ] Task 5: Cache Theme Data (AC: #7)
  - [ ] After clustering + scoring completes, serialize all themes to JSON
  - [ ] Store in Redis under key `macro:themes:all` with TTL 300 seconds (5 min)
  - [ ] Use utils/cache.py helpers from Story 1.1
- [ ] Task 6: Integration with Ingestion Pipeline
  - [ ] Modify run_ingestion() in news_ingestion.py to call clustering after article storage:
    1. Fetch & store articles (existing)
    2. cluster_articles() (new)
    3. create_or_update_themes() (new)
    4. calculate_temperature() for each theme (new)
    5. Cache updated themes to Redis (new)
    6. Update ingestion_logs.themes_updated count
  - [ ] Update POST /api/ingest to return theme count in response

## Dev Notes

### Architecture Compliance

- **File location:** backend/app/services/theme_clustering.py
- **Database access:** Via models/db.py only
- **Cache:** Redis key `macro:themes:all`, TTL 300s. Use utils/cache.py helpers.
- **Naming:** snake_case for all functions, variables. PascalCase for class names only.
- **Score labels:** 'hot', 'warm', 'cool' — NOT 'warming'

### Why Keyword-Based Clustering (Not ML)

The architecture doc notes "No specific clustering algorithm chosen" as a minor gap. For the hackathon:
- **TF-IDF + cosine similarity** would be more accurate but adds complexity and requires scikit-learn
- **Keyword matching** against predefined themes is simpler, deterministic, and demo-friendly
- Can always upgrade to ML-based clustering post-hackathon
- Predefined themes ensure we always get recognizable names (not "Cluster 7")

### Slug Generation

```python
import re

def generate_slug(name):
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')
```

### SQL Patterns

```python
# Create theme
INSERT INTO themes (name, slug, description, score_label, score_value, article_count, first_seen_at, last_updated_at)
VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
ON CONFLICT (slug) DO UPDATE SET
    score_label = EXCLUDED.score_label,
    score_value = EXCLUDED.score_value,
    article_count = EXCLUDED.article_count,
    last_updated_at = NOW()

# Update article theme assignment
UPDATE articles SET theme_id = %s WHERE id = %s

# Count articles by recency for scoring
SELECT
    COUNT(*) FILTER (WHERE published_at >= NOW() - INTERVAL '24 hours') as last_24h,
    COUNT(*) FILTER (WHERE published_at >= NOW() - INTERVAL '72 hours' AND published_at < NOW() - INTERVAL '24 hours') as last_72h,
    COUNT(*) FILTER (WHERE published_at < NOW() - INTERVAL '72 hours') as older
FROM articles WHERE theme_id = %s
```

### Previous Story Dependencies

- Story 1.1: Database schema, Redis connection, Flask app
- Story 1.2: Articles exist in the database from ingestion pipeline, run_ingestion() function

### NFR Compliance

- NFR13: Clustering produces 5-15 distinct themes — enforce by having 15 predefined themes and only creating those with matches
- NFR5: Clustering + scoring must complete within the 60-second ingestion window

### Critical Warnings

- **DO NOT** use scikit-learn, NLTK, or any ML library — keep it simple with keyword matching
- **DO NOT** create region_tags or asset_tags — that's Story 2.1
- **DO NOT** generate causal chains — that's Story 3.1
- **DO NOT** generate article summaries — that's Story 2.3
- **DO NOT** delete or recreate themes on each run — UPDATE existing themes
- **DO NOT** use 'warming' as a score_label — the correct value is 'warm'

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.3]
- [Source: _bmad-output/planning-artifacts/prd.md#FR6-FR7-FR10]

## Dev Agent Record

### Agent Model Used



### Debug Log References

### Completion Notes List

### File List
