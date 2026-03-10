---
title: 'Market Signals Tab — Asset Class Swimlanes'
slug: 'market-signals-tab'
created: '2026-03-10'
status: 'implementation-complete'
stepsCompleted: [1, 2, 3, 4]
tech_stack: [Python 3.14, Flask 3.1, PostgreSQL 16 (raw SQL via psycopg2), React 19, Tailwind CSS 4]
files_to_modify: [frontend/src/components/ThemeFeed.jsx, frontend/src/pages/DashboardPage.jsx, frontend/src/api/client.js, frontend/src/components/MarketSignalsPanel.jsx (new), backend/app/routes/signals.py (new), backend/app/__init__.py]
code_patterns: [Flask Blueprint + execute_query, activeTab state in DashboardPage controls main panel, onTabChange callback from ThemeFeed to parent, api.get() in client.js]
test_patterns: [No test files exist in the project]
---

# Tech-Spec: Market Signals Tab — Asset Class Swimlanes

**Created:** 2026-03-10

## Overview

### Problem Statement

Articles that don't match any of the 21 Watch List narrative themes but carry asset class tags (Equities, Bonds, FX, Commodities, Crypto, Real Estate) are currently invisible to users. The three-tier routing marks them as "Market Signals-ready" (`theme_id = NULL`, `asset_tags` present) but there's no UI to browse them.

### Solution

Add a "Market Signals" tab in the sidebar (positioned between Watch List and Memory Search) that, when selected, displays unthemed articles with asset tags in vertical swimlane columns in the main panel. Sidebar provides date range filter and multi-select asset class filter (default: all selected) that dynamically controls which swimlane columns appear. Clicking an article opens its URL in a new browser tab.

### Scope

**In Scope:**
- New "Market Signals" tab in sidebar between Watch List and Memory Search
- New API endpoint to fetch unthemed articles grouped by asset class
- Swimlane UI in main panel with dynamic columns based on asset class selection
- Multi-select asset class filter in sidebar (default: all 6 selected, with Clear All / Select All toggle)
- Compact article cards (title, source, time)
- Date range filter in sidebar
- Click article → open URL in new tab

**Out of Scope:**
- Article detail view within the app
- Sorting/reordering within swimlanes
- Changes to the Watch List or Memory Search tabs

## Context for Development

### Codebase Patterns

- **Sidebar tabs**: `ThemeFeed.jsx` uses `activeTab` local state (`'live'` / `'memory'`), parent notified via `onTabChange?.(tab)` callback
- **Asset classes**: 6 classes defined in `tagging.py` — Equities, Bonds, FX, Commodities, Crypto, Real Estate. Stored as `TEXT[]` in `articles.asset_tags`
- **Three-tier routing**: `theme_id IS NULL AND asset_tags IS NOT NULL` = Market Signals candidates
- **API patterns**: Flask Blueprint routes, `execute_query()` for DB, JSON responses with `{"data": ..., "meta": {...}}`
- **Frontend API**: `client.js` exports fetch functions, components consume via props or direct calls
- **Article cards**: `ArticleCard.jsx` exists with source domain mapping, image support

### Files to Modify

| File | Change |
| ---- | ------ |
| `frontend/src/components/ThemeFeed.jsx` | Add 3rd "Market Signals" tab between Watch List and Memory Search |
| `frontend/src/pages/DashboardPage.jsx` | Add `signals` case to `activeTab` rendering, import & render `MarketSignalsPanel` |
| `frontend/src/api/client.js` | Add `fetchMarketSignals({ from, to })` function |
| `frontend/src/components/MarketSignalsPanel.jsx` | **NEW** — 6-column swimlane grid with date filter |
| `backend/app/routes/signals.py` | **NEW** — Blueprint with `/api/signals` endpoint |
| `backend/app/__init__.py` | Register `signals_bp` Blueprint |

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `frontend/src/components/ArticleCard.jsx` | Existing card component — reference only, too heavy for compact cards |
| `backend/app/routes/themes.py` | Flask Blueprint pattern reference |
| `backend/app/services/tagging.py` | Asset class definitions (Equities, Bonds, FX, Commodities, Crypto, Real Estate) |
| `backend/app/models/db.py` | `execute_query()` for all DB access |

### Anchor Points

**DashboardPage.jsx** — Parent controls main panel:
- `activeTab` state: `'live'` → ThemeDetailPanel, `'memory'` → MemoryDetailPanel
- Need to add `'signals'` → MarketSignalsPanel
- ThemeFeed notifies parent via `onTabChange(tab)` callback

**ThemeFeed.jsx** — Sidebar tab system:
- Local `activeTab` state (`'live'` / `'memory'`), needs 3rd value `'signals'`
- Tab bar is `<div className="flex border-b border-slate-700">` with flex-1 buttons
- 3 tabs fit at `text-xs` or abbreviated labels

**client.js** — API pattern:
- `const api = axios.create({ baseURL: '/api' })`
- Pattern: `export const fetchX = (params) => api.get('/endpoint', { params })`

**Blueprint registration** — `__init__.py`:
- Pattern: `from app.routes.X import X_bp` then `app.register_blueprint(X_bp)`

**SQL for Market Signals articles**:
```sql
SELECT id, title, url, source_name, published_at, asset_tags
FROM articles
WHERE theme_id IS NULL
  AND asset_tags IS NOT NULL
  AND published_at >= %s AND published_at < %s
ORDER BY published_at DESC
LIMIT 200
```
- Articles can have multiple asset_tags (TEXT[]) — an article tagged `{Equities, Bonds}` appears in both swimlanes
- Group by asset class in Python: iterate articles, append to each matching class list

### Technical Decisions

- **Swimlanes in main panel** — 320px sidebar is too narrow for 6 columns. Tab lives in sidebar, swimlane view renders in main panel area.
- **Compact cards** — fastest to implement. Title + source + relative time. No images or summaries. Hover tooltip shows full title.
- **State lifted to DashboardPage** — Date filters and asset class selection state owned by DashboardPage, passed down to both ThemeFeed (sidebar controls) and MarketSignalsPanel (filtering). This enables sidebar controls to drive main panel behavior.
- **Asset class multi-select in sidebar** — Checkbox-style buttons for each of 6 asset classes. Clear All / Select All toggle. Selected classes determine which swimlane columns render (dynamic `grid-template-columns`). Columns expand to fill available width as fewer are selected.
- **Default to last 30 days** — If no `from` param, backend defaults to `NOW() - INTERVAL '30 days'`. Prevents loading thousands of articles on first view.
- **SQL LIMIT 200** — Cap total results to prevent performance issues on broad date ranges. ~33 per swimlane is plenty for browsing.
- **Click → new tab** — `window.open(url, '_blank', 'noopener,noreferrer')`, no in-app detail view.
- **Group in Python** — Single SQL query returns all matching articles; backend groups by asset_tag into 6 arrays in the response. Frontend receives pre-grouped data.
- **No AI digest** — Initially implemented Claude Haiku-generated market digest; removed in favor of asset class filter for simpler, faster UX without API latency or rate limiting concerns.

## Implementation Plan

### Task 1: Backend — Create Market Signals API endpoint

- [x] Task 1: Create `/api/signals` endpoint returning articles grouped by asset class
  - File: `backend/app/routes/signals.py` **(NEW)**
  - Action: Create new Flask Blueprint `signals_bp` with route `GET /api/signals`
  - Query params: `from` (date string, optional), `to` (date string, optional)
  - SQL: `SELECT id, title, url, source_name, published_at, asset_tags FROM articles WHERE theme_id IS NULL AND asset_tags IS NOT NULL` + date filters + `ORDER BY published_at DESC LIMIT 200`
  - Response grouping: Iterate results, for each article append to every matching asset class bucket. Return `{"data": {"Equities": [...], "Bonds": [...], "FX": [...], "Commodities": [...], "Crypto": [...], "Real Estate": [...]}, "meta": {"total_articles": N}}` where `total_articles` = unique article count from SQL (before grouping, not sum of bucket sizes)
  - Each article object: `{"id", "title", "url", "source_name", "published_at"}` (drop `asset_tags` from response items — frontend doesn't need it)
  - Date handling: If `from` provided, add `AND published_at >= %s`. If `to` provided, use exclusive upper bound: `AND published_at < %s` where the value is `to + 1 day` (avoids midnight truncation — e.g., `to=2026-03-31` becomes `< 2026-04-01`). **Default: if no `from`, default to 30 days ago** (`datetime.now(timezone.utc) - timedelta(days=30)`).
  - Serialization: Explicitly convert each article's `published_at` datetime to ISO string (`row["published_at"].isoformat()`) before adding to response dict.
  - LIMIT: Always append `LIMIT 200` to the query to cap results.
  - Error handling: Wrap in try/except, return `{"error": True, "message": str(e), "code": "SIGNALS_ERROR"}` with status 500 on failure. Follow `themes.py` pattern.
  - Input validation: Parse `from`/`to` with `datetime.strptime(val, '%Y-%m-%d')`. If malformed, return 400 with `{"error": True, "message": "Invalid date format, use YYYY-MM-DD"}`.
  - Notes: Use `execute_query()` from `app.models.db`.

### Task 2: Backend — Register Blueprint

- [x] Task 2: Register `signals_bp` in app factory
  - File: `backend/app/__init__.py`
  - Action: Add `from app.routes.signals import signals_bp` and `app.register_blueprint(signals_bp)` following existing pattern

### Task 3: Frontend — Add API client function

- [x] Task 3: Add `fetchMarketSignals` to API client
  - File: `frontend/src/api/client.js`
  - Action: Add `export const fetchMarketSignals = (params) => api.get('/signals', { params })`
  - Params: `{ from: 'YYYY-MM-DD', to: 'YYYY-MM-DD' }` (both optional)

### Task 4: Frontend — Add "Market Signals" tab to sidebar

- [x] Task 4: Add 3rd tab button in ThemeFeed sidebar
  - File: `frontend/src/components/ThemeFeed.jsx`
  - Action: Add a "Signals" tab button between "Watch List" and "Memory Search" in the tab bar
  - The new button sets `activeTab` to `'signals'` and calls `onTabChange?.('signals')`
  - Reduce tab text to fit 3 tabs in 320px: keep "Watch List", use "Signals" (not "Market Signals"), keep "Memory"
  - Sidebar body uses 3-way ternary: `activeTab === 'live' ? (...) : activeTab === 'signals' ? (...) : (...)`
  - Signals tab sidebar body contains: date range filter (month inputs) + asset class multi-select (6 checkbox-style buttons with Clear All / Select All toggle)
  - Props received from DashboardPage: `signalsFromDate`, `signalsToDate`, `onSignalsFromDateChange`, `onSignalsToDateChange`, `allAssetClasses`, `selectedAssetClasses`, `onSelectedAssetClassesChange`

### Task 5: Frontend — Create MarketSignalsPanel component

- [x] Task 5: Build the 6-column swimlane panel with date filter
  - File: `frontend/src/components/MarketSignalsPanel.jsx` **(NEW)**
  - Action: Create component that fetches and displays market signals articles in 6 swimlane columns
  - **Layout:**
    - No header bar — date filter and asset class controls live in sidebar
    - Dynamic grid columns based on `selectedAssetClasses` prop (`gridTemplateColumns: repeat(N, minmax(0, 1fr))`)
    - Each column scrolls independently (`overflow-y-auto`)
    - Empty state when no asset classes selected: "Select at least one asset class to view signals."
  - **Data flow (props-driven):**
    - Receives `fromDate`, `toDate`, `selectedAssetClasses` from DashboardPage
    - Component owns `data`, `loading`, `error` state
    - On mount and when date filters change, call `fetchMarketSignals({ from, to })` (debounced 300ms via useEffect with AbortController)
    - Filters `SWIMLANES` array by `selectedAssetClasses` to determine visible columns
    - Response: `{ data: { Equities: [...], Bonds: [...], FX: [...], Commodities: [...], Crypto: [...], "Real Estate": [...] } }`
  - **Compact article card (inline, not separate component):**
    - Title (truncated to 2 lines with `line-clamp-2`)
    - Source name (`source_name`) + relative time (e.g., "Reuters · 2h ago") in `text-xs text-slate-400`
    - Entire card clickable → `window.open(article.url, '_blank')`
    - Hover: `bg-slate-700/50` transition
    - Style: `bg-[#1e293b] rounded-lg p-3 cursor-pointer`
  - **Column headers:** Equities (blue), Bonds (green), FX (amber), Commodities (orange), Crypto (purple), Real Estate (teal) — use colored left border or badge
  - **Column order:** Equities, Bonds, FX, Commodities, Crypto, Real Estate (fixed order, hardcoded in frontend)
  - **Empty state:** If a column has 0 articles, show "No signals" placeholder
  - **Loading state:** Show "Loading..." centered in panel while fetching
  - **Date defaults:** On first load, no date params sent — backend defaults to last 30 days

### Task 6: Frontend — Wire MarketSignalsPanel into DashboardPage

- [x] Task 6: Render MarketSignalsPanel when signals tab is active
  - File: `frontend/src/pages/DashboardPage.jsx`
  - Action: Import `MarketSignalsPanel` and add conditional rendering when `activeTab === 'signals'`
  - **Restructuring required:** The main panel currently uses a binary ternary: `activeTab === 'memory' ? <MemoryDetailPanel> : <ThemeDetailPanel>`. Refactor to nested ternaries or a helper function:
    ```jsx
    {activeTab === 'signals' ? (
      <MarketSignalsPanel fromDate={signalsFromDate} toDate={signalsToDate} selectedAssetClasses={selectedAssetClasses} />
    ) : activeTab === 'memory' ? (
      <MemoryDetailPanel ... />
    ) : (
      <ThemeDetailPanel ... />
    )}
    ```
  - DashboardPage owns lifted state: `signalsFromDate`, `signalsToDate`, `selectedAssetClasses` (default: all 6). Passes down to both ThemeFeed (sidebar controls) and MarketSignalsPanel (data display/filtering).

## Acceptance Criteria

- [x] AC 1: Given the sidebar, when I look at the tabs, then I see three tabs: "Watch List", "Signals", "Memory" in that order
- [x] AC 2: Given I click the "Signals" tab, when the main panel renders, then I see swimlane columns for all selected asset classes (default: all 6)
- [x] AC 3: Given articles exist with `theme_id IS NULL AND asset_tags IS NOT NULL`, when I view Market Signals, then those articles appear in the correct swimlane columns based on their asset_tags
- [x] AC 4: Given an article has `asset_tags = {Equities, Bonds}`, when I view Market Signals, then that article appears in both the Equities and Bonds columns
- [x] AC 5: Given I set a date range filter in the sidebar, when the panel re-fetches, then only articles within that date range are shown
- [x] AC 6: Given I click an article card, when the click fires, then the article URL opens in a new browser tab
- [x] AC 7: Given a swimlane column has no articles, when I view it, then I see a "No signals" empty state message
- [x] AC 8: Given I call `GET /api/signals`, when no date params are provided, then articles from the last 30 days with asset_tags are returned grouped by asset class (max 200)
- [x] AC 9: Given I call `GET /api/signals?from=2026-03-01&to=2026-03-31`, when the response returns, then only articles published in March 2026 are included
- [x] AC 10: Given I switch to the Signals tab, when data is being fetched, then I see a loading indicator in the main panel
- [x] AC 11: Given the sidebar on Signals tab, when I deselect an asset class, then its swimlane column disappears and remaining columns expand to fill available width
- [x] AC 12: Given all asset classes are deselected, when I view the main panel, then I see "Select at least one asset class to view signals."
- [x] AC 13: Given the sidebar asset class filter, when I click "Clear All", all checkboxes deselect; when I click "Select All", all checkboxes select

## Dependencies

- **Three-tier routing must be active** — articles need `theme_id = NULL` and `asset_tags` populated. This depends on the Watch List Theme Overhaul (Epic 1) being complete with reclassification run.
- **No new external libraries** — uses existing React, Tailwind, axios, Flask stack.
- **Database** — reads from existing `articles` table. No schema changes needed.

## Testing Strategy

- **Manual testing:** Navigate to Signals tab, verify swimlanes load, click articles, test date filter
- **API testing:** `curl http://localhost:5001/api/signals` and `curl "http://localhost:5001/api/signals?from=2026-03-01&to=2026-03-31"` — verify JSON structure
- **Edge cases:** Empty swimlanes, articles with multiple asset_tags, no date filter vs. narrow date range

## Notes

- **Risk:** If reclassification assigns most articles to themes, Market Signals may have few articles. This is expected — only truly unthemed articles with asset tags appear here.
- **Limitation:** SQL LIMIT 200 caps total results (not per-swimlane). If one asset class dominates, other columns may appear sparse. Acceptable for hackathon — could use UNION ALL with per-class limits later.
- **Future:** Could allow promoting a Market Signal article to a Watch List theme.


