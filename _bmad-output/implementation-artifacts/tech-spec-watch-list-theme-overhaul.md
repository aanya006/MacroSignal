---
title: 'Watch List Theme Overhaul — Curated Narratives + Claude Classification'
slug: 'watch-list-theme-overhaul'
created: '2026-03-10'
status: 'completed'
stepsCompleted: [1, 2, 3, 4]
tech_stack: [Python 3.14, Flask 3.1, Anthropic SDK (Haiku claude-haiku-4-5-20251001), PostgreSQL 16 (raw SQL via psycopg2), Redis 7, React 19, Zustand, Tailwind CSS 4]
files_to_modify: [backend/app/services/theme_clustering.py, backend/app/services/theme_classifier.py (new), backend/app/routes/ingestion.py, frontend/src/components/ThemeFeed.jsx]
code_patterns: [Anthropic lazy-init _get_client(), execute_query() for all DB, cache_get/cache_set for Redis, classify_article() returns list of slug strings, ON CONFLICT upsert pattern]
test_patterns: [No test files exist in the project]
---

# Tech-Spec: Watch List Theme Overhaul — Curated Narratives + Claude Classification

**Created:** 2026-03-10

## Overview

### Problem Statement

The current theme clustering uses 15 generic category-style themes (e.g., "Geopolitical Risk", "Global Trade & Tariffs") that don't match how asset managers think. They organize the world around specific, named macro narratives — "Russia-Ukraine War & European Security", "US-China Tariffs & Tech Decoupling", "Europe Rearmament & Defense Capex". The generic labels reduce the product's credibility and usefulness for the target audience.

### Solution

Replace `THEME_DEFINITIONS` with 21 curated narrative themes that reflect how asset managers actually think about macro risks. Add Claude Haiku-powered article classification with broad keyword fallback. Implement three-tier article routing: Watch List (theme match), Market Signals-ready (asset class tags only), and not surfaced (no relevance). Reclassify all existing articles. Rename "Live Themes" tab to "Watch List".

### Scope

**In Scope:**
- New 21-theme Watch List definitions with broad keyword fallback
- Claude Haiku-powered article classification integrated into ingestion pipeline
- Three-tier article routing (Watch List / Market Signals-ready / not surfaced)
- Reclassify all existing articles against new themes (wipe old assignments, reclassify everything)
- Rename "Live Themes" tab → "Watch List" in frontend

**Out of Scope:**
- Market Signals tab UI (separate spec)
- Claude suggesting new/emerging themes (future iteration)
- Changes to causal chain generation, article summaries, or memory search
- Database schema changes

## Context for Development

### Codebase Patterns

- **Anthropic client**: Lazy-init `_get_client()` pattern used in `summarizer.py` and `causal_chain.py` — model ID `claude-haiku-4-5-20251001`
- **DB access**: All via `execute_query()` from `app.models.db` — raw SQL, no ORM. `execute_many()` also available.
- **Redis**: `cache_set(key, value, ttl)` / `cache_get(key)` from `app.utils.cache`
- **Classification flow**: `classify_article(article)` returns `list[str]` of theme slugs → `cluster_articles()` picks first match → sets `theme_id` FK
- **Pipeline order**: `run_ingestion()` → fetch → keyword filter → `store_articles()` (sets region_tags/asset_tags via `tagging.py`) → `run_clustering()` (classify → score → tag → causal chains → snapshot → cache) → summarize
- **Theme upsert**: `create_or_update_themes()` uses `ON CONFLICT (slug) DO UPDATE SET` (updated from DO NOTHING)
- **Tagging**: `tagging.py` already classifies articles into regions (Singapore, US, China, ASEAN, EU, Japan) and asset classes (Equities, Bonds, FX, Commodities) using regex patterns — set during `store_articles()`
- **Frontend**: Tabs via local `activeTab` state in `ThemeFeed.jsx`. snake_case everywhere.
- **Error handling**: All Claude API calls wrapped in try/except with specific handlers for `RateLimitError`, `APITimeoutError`

### Files to Reference

| File | Purpose | Key Details |
| ---- | ------- | ----------- |
| `backend/app/services/theme_clustering.py` | **Primary target** — THEME_DEFINITIONS, classify_article(), create_or_update_themes(), run_clustering() | 342 lines, all theme logic lives here |
| `backend/app/services/summarizer.py` | Anthropic client reference pattern | `_get_client()`, error handling, rate limit sleep |
| `backend/app/services/causal_chain.py` | Another Anthropic reference — JSON response parsing | Same `_get_client()` pattern, structured prompt |
| `backend/app/services/news_ingestion.py` | Ingestion pipeline — calls `run_clustering()` | `run_ingestion()` is the entry point |
| `backend/app/services/tagging.py` | Region/asset tagging — already sets `region_tags`/`asset_tags` on articles | Used for three-tier routing (articles with asset_tags but no theme = Market Signals) |
| `frontend/src/components/ThemeFeed.jsx` | Tab label at line 114 | Single string change: "Live Themes" → "Watch List" |
| `backend/app/utils/config.py` | `ANTHROPIC_API_KEY` already exported | No changes needed |
| `backend/app/models/db.py` | `execute_query()` and `execute_many()` | Used for all DB operations |

### Technical Decisions

- **Claude Haiku** (`claude-haiku-4-5-20251001`) for classification — low cost (~$0.01/batch), sufficient quality
- **Broad keyword fallback** — not precise per-theme keywords, just a safety net when Claude is unavailable. Groups of broad keywords covering all 21 themes to at least get articles into the right neighborhood.
- **Wipe and reclassify** — on deployment: `UPDATE articles SET theme_id = NULL`, delete theme_history rows (FK has no CASCADE), delete old theme rows, insert new 21 themes, run full classification. **Note: this wipes theme_history — historical snapshots for old themes are lost. New snapshots will build from reclassification onward.**
- **Three-tier routing** needs no schema changes — articles already have nullable `theme_id` and `asset_tags[]`. Logic: theme_id set = Watch List; theme_id NULL + asset_tags present = Market Signals-ready; theme_id NULL + no asset_tags = not surfaced
- **New file `theme_classifier.py`** — separates Claude classification logic from clustering orchestration to keep `theme_clustering.py` clean
- **Claude suggestion of new themes** deferred to future iteration
- **`classify_article()` interface unchanged** — still returns `list[str]` of slugs for backward compatibility with `cluster_articles()`

## Implementation Plan

### Tasks

- [x] **Task 1: Create `backend/app/services/theme_classifier.py` — Claude-powered classification module**
  - File: `backend/app/services/theme_classifier.py` (NEW)
  - Action: Create new module with:
    - `_get_client()` — lazy-init Anthropic client (same pattern as `summarizer.py`)
    - `CLASSIFICATION_PROMPT` — prompt template that instructs Claude to classify an article into one of the 21 theme slugs. The prompt must include the full list of theme slugs and names so Claude knows the valid options. Claude should return JSON: `{"theme_slug": "<slug>", "confidence": 0.0-1.0}`. If no theme fits, return `{"theme_slug": null, "confidence": 0.0}`.
    - `classify_article_with_claude(title, text)` — sends article title + first **1000** chars of text to Claude Haiku, parses JSON response. **Confidence threshold: 0.5** — if confidence < 0.5, treat as no match (return None). Returns theme slug string or None. **Guard: `if not client: return None`** (same as `summarizer.py` line 33-35, handles missing API key). Handles `RateLimitError` (sleep 10s + return None), `APITimeoutError` (return None), JSON parse errors (return None). **No sleep inside this function** — rate-limit delay is handled in the calling loop (see Task 3).
  - Notes: Keep classification prompt concise — Claude Haiku performs better with shorter, direct prompts. Include the 21 theme slugs and 1-line descriptions in the prompt so Claude has context. No batch function needed — `classify_article()` in `theme_clustering.py` calls this per-article during `cluster_articles()` iteration.

- [x] **Task 2: Replace `THEME_DEFINITIONS` in `theme_clustering.py` with 21 curated narrative themes**
  - File: `backend/app/services/theme_clustering.py`
  - Action: Replace the entire `THEME_DEFINITIONS` dict with the new 21 themes. Each theme entry must have: `name` (display name), `keywords` (broad fallback keywords), `description` (1-line description for Claude prompt context). Remove the `"general-macro"` catch-all theme.
  - New themes (slug → name):
    - `us-policy-regime-shift` → "US Policy Regime Shift (Trump 2.0 / DOGE)"
    - `us-china-tariffs-tech-decoupling` → "US-China Tariffs & Tech Decoupling"
    - `us-fed-rate-path` → "US Fed Rate Path & Forward Guidance"
    - `europe-rearmament-defense` → "Europe Rearmament & Defense Capex"
    - `ai-disruption-compute` → "AI Disruption & Compute Infrastructure"
    - `middle-east-conflict-energy` → "Middle East Conflict & Energy Risk"
    - `russia-ukraine-european-security` → "Russia-Ukraine War & European Security"
    - `china-economic-slowdown` → "China Economic Slowdown & Property Crisis"
    - `china-pboc-stimulus` → "China PBOC Stimulus & Monetary Easing"
    - `critical-minerals-semiconductors` → "Critical Minerals & Semiconductor Supply"
    - `global-sovereign-debt` → "Global Sovereign Debt & Fiscal Sustainability"
    - `emerging-market-stress` → "Emerging Market Currency & Debt Stress"
    - `india-growth-ascent` → "India's Growth Ascent"
    - `opec-oil-supply` → "OPEC+ Production & Oil Supply Politics"
    - `labor-immigration-demographics` → "Labor Markets, Immigration & Demographics"
    - `credit-shadow-banking` → "Credit Conditions & Shadow Banking Risk"
    - `nuclear-energy-renaissance` → "Nuclear Energy Renaissance"
    - `boj-yen-dynamics` → "BOJ Policy Normalization & Yen Dynamics"
    - `de-dollarization` → "De-dollarization & Reserve Currency Shifts"
    - `china-taiwan-indo-pacific` → "China-Taiwan Tensions & Indo-Pacific Security"
    - `mas-sgd-policy` → "MAS Policy & SGD Management"
  - Notes: Keywords should be broad — 5-8 keywords per theme covering the major terms. These are only used when Claude is unavailable. Example for `us-fed-rate-path`: `["federal reserve", "fed rate", "fomc", "powell", "fed funds", "rate cut", "rate hike", "fed policy"]`.

- [x] **Task 3: Rewrite `classify_article()` and update `cluster_articles()` in `theme_clustering.py`**
  - File: `backend/app/services/theme_clustering.py`
  - Action (classify_article): Rewrite `classify_article(article)` to:
    1. First attempt: Call `classify_article_with_claude(title, text)` from `theme_classifier.py`
    2. If Claude returns a valid slug → return `[slug]`
    3. If Claude returns None (API failure, timeout, low confidence) → fall back to keyword matching against new `THEME_DEFINITIONS`
    4. If keyword matching also finds no match → return empty list `[]` (article stays unthemed — three-tier routing will handle it)
  - Action (cluster_articles): Modify `cluster_articles()` so that when `classify_article()` returns an empty list, the article's `theme_id` remains NULL (skip the UPDATE). Currently the code does `best_match = matches[0]` which would crash on an empty list. Add a guard: `if not matches: continue`. **Add `time.sleep(0.3)` in the article loop** after each `classify_article()` call — same pattern as `summarizer.py` line 123 which puts the delay in the outer loop, not inside the per-article function.
  - Notes: Remove the `"general-macro"` fallback. Articles that match nothing are intentionally left unthemed. The function signature and return type (`list[str]`) stay the same for backward compatibility with `cluster_articles()`. Articles left with `theme_id = NULL` are intentionally routed to Market Signals (if they have asset_tags) or not surfaced (if they have no asset_tags). This is the three-tier routing mechanism. **Grep all callers of `classify_article()` and `cluster_articles()` before modifying to ensure no other call sites are affected.**

- [x] **Task 4: Update `create_or_update_themes()` to upsert correctly**
  - File: `backend/app/services/theme_clustering.py`
  - Action: Change the upsert from `ON CONFLICT (slug) DO NOTHING` to `ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description` so that re-running the function updates existing theme rows with new names/descriptions instead of silently skipping them. Since we replaced the dict in Task 2, this function will automatically create the new 21 themes.

- [x] **Task 5: Add reclassification function**
  - File: `backend/app/services/theme_clustering.py`
  - Action: Add `reclassify_all_articles()` function with these steps:
    **Wipe phase (steps 1-3) — use `get_connection()` directly for a single transaction:**
    ```python
    from app.models.db import get_connection, release_connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE articles SET theme_id = NULL")
            cur.execute("DELETE FROM theme_history WHERE theme_id IN (SELECT id FROM themes)")
            cur.execute("DELETE FROM themes")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)
    ```
    **`execute_query()` auto-commits per call on separate connections (see `db.py` line 24-38) — it CANNOT do multi-statement transactions.** The wipe steps must share one connection.
    **Rebuild phase (steps 4-9) — normal `execute_query()` calls are fine:**
    4. Calls `cluster_articles()` (internally calls `create_or_update_themes()` at line 130, so no separate call needed)
    5. Calls `calculate_temperatures()` (rescore all themes)
    6. Calls `aggregate_theme_tags()` (re-aggregate region/asset tags to theme level)
    7. Calls `generate_chains_for_hot_themes()` (from `app.services.causal_chain` — same import + try/except as `run_clustering()` line 324-326, so hot themes have causal chains immediately)
    8. Calls `snapshot_themes()` (initial snapshot for new themes — so Memory Search has data right away)
    9. Calls `cache_themes()` (refresh Redis cache)
    10. Returns summary: `{"articles_assigned": N, "themes_created": 21}` (N = count from `cluster_articles()` — articles matched to a theme, not total processed)
  - Notes: This function is called once manually (or via a one-time API endpoint) after deployment. NOT called on every ingestion cycle. **Critical: `theme_history.theme_id REFERENCES themes(id)` has NO CASCADE — step 2 must delete theme_history rows before step 3 deletes themes, or the DELETE will fail with a FK violation. Note: `cluster_articles()` already calls `create_or_update_themes()` internally (line 130), so no separate call is needed — avoids redundant upsert.**

- [x] **Task 6: Add reclassification API endpoint**
  - File: `backend/app/routes/ingestion.py` (use existing file — follows the project's pattern of co-locating ingestion-related routes)
  - Action: Add `POST /api/admin/reclassify` endpoint that calls `reclassify_all_articles()` and returns the summary. This is a dev/admin endpoint for one-time use.
  - Notes: Keep it simple — no auth needed (hackathon prototype). Log the operation. Use `ingestion.py` as the blueprint since reclassification is an ingestion-adjacent operation.

- [x] **Task 7: Update `cache_themes()` to exclude themes with zero articles**
  - File: `backend/app/services/theme_clustering.py`
  - Action: Verify `cache_themes()` already filters `WHERE article_count > 0`. It does (confirmed in investigation). No change needed — but verify after reclassification that themes with 0 articles don't show up in the API response.

- [x] **Task 8: Rename "Live Themes" → "Watch List" in frontend**
  - File: `frontend/src/components/ThemeFeed.jsx`
  - Action: Change line 114 from `Live Themes` to `Watch List`. Single string replacement.

- [x] **Task 9: Update `QUICK_FILTERS` and hint text in ThemeFeed.jsx**
  - File: `frontend/src/components/ThemeFeed.jsx`
  - Action: Replace `QUICK_FILTERS` (line 6) with 5 items using shorter labels that match the new narrative themes: `['Fed', 'Trump', 'China', 'AI', 'Defense']`. Keep to 5 items max to avoid chip overflow on smaller viewports. **Also update the hint text at line 233** (`"Try: Fed Rate, MAS, China, Japan, Semiconductor"`) to match: `"Try: Fed, Trump, China, AI, Defense"`.

### Acceptance Criteria

- [ ] **AC1:** Given the new `THEME_DEFINITIONS` exists in `theme_clustering.py`, when I count the theme entries, then there are exactly 21 themes (no more, no less) and no `"general-macro"` catch-all.

- [ ] **AC2:** Given an article about "Federal Reserve raises interest rates by 25 basis points", when `classify_article()` is called with Claude available, then it returns `["us-fed-rate-path"]` via Claude classification.

- [ ] **AC3:** Given an article about "Federal Reserve raises interest rates", when `classify_article()` is called with Claude unavailable (API timeout), then it falls back to keyword matching and returns `["us-fed-rate-path"]`.

- [ ] **AC4:** Given an article about "Local celebrity opens new restaurant in Singapore", when `classify_article()` is called, then it returns `[]` (empty list — no theme match from Claude or keywords).

- [ ] **AC5:** Given `classify_article()` returns `[]` for an article, when `cluster_articles()` processes it, then the article's `theme_id` remains NULL in the database (no UPDATE is issued for that article).

- [ ] **AC6:** Given reclassification has run, when querying `SELECT COUNT(*) FROM articles WHERE theme_id IS NULL AND asset_tags IS NOT NULL AND asset_tags != '{}'`, then the count is >= 0 (Market Signals candidates exist as expected). When querying `GET /api/themes`, none of these unthemed articles appear in any theme's article list.

- [ ] **AC7:** Given the `reclassify_all_articles()` function is called, when it completes, then all articles have been reassessed against the 21 new themes, old themes are deleted, new themes exist in the DB, and temperature scores are recalculated.

- [ ] **AC8:** Given the frontend loads, when I look at the left panel tabs, then the first tab reads "Watch List" (not "Live Themes").

- [ ] **AC9:** Given Claude API returns an invalid JSON response during classification, when `classify_article_with_claude()` handles it, then it returns None (no crash) and the system falls back to keyword matching.

- [ ] **AC10:** Given Claude API rate limit is hit during classification, when `classify_article_with_claude()` encounters `RateLimitError`, then it sleeps 10 seconds and returns None (no crash), and the system falls back to keyword matching for that article.

## Additional Context

### Dependencies

- **Anthropic SDK** — already in `requirements.txt`. No new package needed.
- **ANTHROPIC_API_KEY** — must be set in `.env`. Already configured.
- **PostgreSQL** — must be running with existing schema. No schema changes.
- **Redis** — must be running for theme caching. Already configured.

### Testing Strategy

- **Manual testing — reclassification:**
  1. Start backend locally
  2. Call `POST /api/admin/reclassify`
  3. Verify response shows articles reclassified count and 21 themes created
  4. Call `GET /api/themes` and verify new theme names appear
  5. Verify themes are ranked by temperature (hot first)

- **Manual testing — Claude classification:**
  1. Trigger ingestion via `POST /api/ingest`
  2. Check logs for Claude classification calls
  3. Verify new articles are assigned to appropriate narrative themes
  4. Disconnect API key temporarily, trigger ingestion again, verify keyword fallback works

- **Manual testing — three-tier routing:**
  1. After reclassification, query DB: `SELECT COUNT(*) FROM articles WHERE theme_id IS NULL AND asset_tags IS NOT NULL` — these are Market Signals candidates
  2. Query: `SELECT COUNT(*) FROM articles WHERE theme_id IS NULL AND (asset_tags IS NULL OR asset_tags = '{}')` — these are not surfaced
  3. Verify `GET /api/themes` only returns themes with articles (no empty themes)

- **Manual testing — frontend:**
  1. Load dashboard, verify tab says "Watch List"
  2. Verify theme cards show new narrative names
  3. Verify clicking themes still opens detail view with articles, causal chain, timeline

### Notes

- **Risk: Claude classification quality** — If Haiku misclassifies articles, the Watch List loses credibility. Mitigated by: (a) keeping keyword fallback, (b) the prompt includes all 21 theme descriptions for context, (c) confidence threshold of 0.5 filters low-confidence matches.
- **Risk: Reclassification duration** — If there are hundreds of articles, Claude classification one-by-one with 0.3s delays could take minutes. Mitigated by: running reclassification as a one-time admin operation, not during normal ingestion. Future optimization: batch articles in a single prompt.
- **Known limitation** — Articles can only belong to ONE theme (first match). Some articles legitimately span multiple themes (e.g., "PBOC cuts rates amid China property crisis" touches both `china-pboc-stimulus` and `china-economic-slowdown`). The single-theme FK constraint is an existing architectural limitation, not introduced by this change.
- **Future consideration** — Claude-suggested new themes (deferred). When implemented, Claude would return `{"theme_slug": null, "suggested_theme": "Europe Energy Security"}` for articles that don't fit existing themes but form a coherent narrative.
- **Python 3.14** — confirmed as the project runtime (pre-release). Standard library usage only; no 3.14-specific features required by this spec.
- The 21 themes were curated during the Epic 1 retrospective with financial domain expertise.
- Temperature scoring logic stays unchanged — just operates on new themes.
- Causal chain generation stays unchanged — still triggers for hot themes.
- Historical theme snapshots continue working — new themes will start building history.

## Review Notes
- Adversarial code review completed
- Findings: 16 total, 5 fixed, 11 skipped (acceptable for hackathon prototype)
- Resolution approach: auto-fix real bugs
- Fixed: F4 (slug validation), F7 (conditional sleep), F10 (single source of truth), F13 (docstring), F16 (MAS keyword)
- Skipped: F1 (auth), F2/F11 (concurrency), F3/F6 (timeout), F5 (false positive), F8 (thread safety), F9 (prompt injection), F12 (text length), F14 (error leaks), F15 (snapshot conflict)
