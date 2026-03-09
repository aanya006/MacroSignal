---
title: 'Memory Search UI & Historical Parallels'
slug: 'memory-search-ui'
created: '2026-03-09'
status: 'completed'
stepsCompleted: [1, 2, 3, 4]
tech_stack: [React, Tailwind CSS, Zustand, Axios, Flask, PostgreSQL, Redis]
files_to_modify:
  - frontend/src/components/ThemeFeed.jsx
  - frontend/src/api/client.js
  - frontend/src/components/CausalChain.jsx
  - frontend/src/components/ThemeDetailPanel.jsx
  - frontend/src/pages/ThemeDetailPage.jsx
  - frontend/src/pages/DashboardPage.jsx
  - backend/app/routes/memory.py
  - backend/seed_history.py
files_to_create:
  - frontend/src/components/MemorySearchPanel.jsx
  - frontend/src/components/MemoryResultCard.jsx
  - frontend/src/components/MemoryDetailPanel.jsx
  - frontend/src/components/HistoricalParallel.jsx
code_patterns:
  - Functional React components with hooks
  - Tailwind utility classes, dark terminal aesthetic
  - Zustand store with snake_case actions
  - Flask Blueprint + response envelope pattern
  - ThemeFeedCard pattern for result cards
  - CausalChain component pattern for outcome display
test_patterns: []
---

# Tech-Spec: Memory Search UI & Historical Parallels

**Created:** 2026-03-09

## Overview

### Problem Statement

Asset managers cannot search historical themes or discover when similar macro patterns occurred before. The Memory Search tab in the dashboard currently shows "coming soon", and there is no HistoricalParallel component surfacing past parallels on live theme detail views. This limits the product's institutional memory differentiator.

### Solution

Wire up the Memory Search tab with a two-column split layout (search/results left, full detail right) mirroring the Live Themes layout. Add a HistoricalParallel component below the CausalChain on live theme detail views. Extend the backend search API with optional date filtering and causal chain data. Seed backward-looking causal chains for historical themes.

### Scope

**In Scope:**
- Memory Search tab: keyword search, quick filter chips, optional date range refinement
- Two-column layout: result cards (left), detail panel with banner, tags, articles, backward-looking causal chain (right)
- Backward-looking causal chains: "What Happened" header, "Outcome" labels with actual percentages
- HistoricalParallel component on live theme detail (purple accent, dashed separator, "H" icon badge)
- Backend: add from_date/to_date optional params to /api/memory/search, include causal_chain in results
- Seed backward-looking causal chains in seed_history.py
- Debounced search (300ms, min 2 chars)
- Quick filter chips: Fed Rate, MAS Policy, China, Oil, FX

**Out of Scope:**
- Mobile responsiveness
- Advanced historical parallel matching algorithm (use simple searchMemory(theme.name) for now)
- Pagination of search results

## Context for Development

### Codebase Patterns

- React functional components with hooks, Tailwind CSS for styling
- Zustand store for global state (useThemeStore.js) — snake_case actions
- Axios API client at `frontend/src/api/client.js` — `searchMemory(query)` already exists
- Flask Blueprint pattern for API routes, response envelope: `{"data": ..., "meta": {...}}`
- snake_case everywhere (JSON, Python, DB), PascalCase for React components
- Dark terminal aesthetic: `bg-[#0f172a]`, cards `bg-[#1e293b]`, borders `border-slate-700`
- ThemeFeedCard uses `TemperatureBadge` component for Hot/Warm/Cool badges
- DashboardPage renders `<ThemeFeed>` (left) + `<ThemeDetailPanel>` (right) in a flex layout
- ThemeFeed already has tabs (Live/Memory) and search input — Memory tab shows "coming soon"
- CausalChain.jsx uses DIRECTION_CONFIG for Bullish/Bearish/Neutral labels
- ThemeDetailPanel and ThemeDetailPage both render `<CausalChain chain={theme.causal_chain} />` in a 320px right column

### Files to Reference

| File | Purpose |
| ---- | ------- |
| frontend/src/components/ThemeFeed.jsx | Has tabs + "coming soon" — needs major rework for Memory tab |
| frontend/src/components/ThemeFeedCard.jsx | Pattern to follow for MemoryResultCard |
| frontend/src/components/TemperatureBadge.jsx | Reuse for badges on memory results |
| frontend/src/api/client.js | `searchMemory()` exists, needs from/to params |
| frontend/src/components/CausalChain.jsx | Extend with `historical` prop for past-tense labels |
| frontend/src/components/ThemeDetailPanel.jsx | Add HistoricalParallel below CausalChain |
| frontend/src/pages/ThemeDetailPage.jsx | Add HistoricalParallel below CausalChain |
| frontend/src/pages/DashboardPage.jsx | Layout change: when Memory tab active, show MemorySearchPanel instead of ThemeDetailPanel |
| frontend/src/store/useThemeStore.js | Reference for state patterns (don't need to modify) |
| backend/app/routes/memory.py | Add from_date/to_date params, include causal_chain in results |
| backend/seed_history.py | Add causal_chain JSON to each historical theme |
| _bmad-output/planning-artifacts/ux-design-final-mockup.html | Design source of truth |

### Technical Decisions

1. **Architecture change:** When Memory tab is active, the right panel swaps from ThemeDetailPanel to MemoryDetailPanel. DashboardPage needs to track `activeTab` state and conditionally render.
2. **ThemeFeed rework:** ThemeFeed becomes the left column for BOTH tabs. When Memory tab active, it shows search bar + quick chips + date refine + result cards. When Live tab active, it shows existing filter + ThemeFeedCards.
3. **New components:** MemoryResultCard (compact feed card), MemoryDetailPanel (right panel with banner+articles+causal chain), HistoricalParallel (purple section below CausalChain)
4. **CausalChain extension:** Add `historical` prop. When true: header says "What Happened", third section says "Outcome", direction labels show "▲ +X.X%" instead of "▲ Bullish". Needs `change` field in impacts JSON.
5. **Backend:** Add `from_date`, `to_date` optional query params. Add `causal_chain` field to search results (from themes table). Simple WHERE clause additions.
6. **Seed data:** Add `causal_chain` JSON with backward-looking data + `change` fields to all 5 historical themes in seed_history.py.
7. **HistoricalParallel matching:** On live theme detail load, call `searchMemory(theme.name)`, filter out self (same slug), show first result if exists.
8. **Debounce:** Use setTimeout/clearTimeout pattern (no lodash dependency). 300ms delay, min 2 chars.
9. **Quick filter chips:** Hardcoded array: `['Fed Rate', 'MAS Policy', 'China', 'Oil', 'FX']`

## Implementation Plan

### Tasks

**Task 1: Backend — Extend search API + seed causal chains**
- `backend/app/routes/memory.py`: Add `from_date`, `to_date` optional params with WHERE clauses on `t.first_seen_at` and `t.last_updated_at`. Add `t.causal_chain` to SELECT and include in enriched results.
- `backend/seed_history.py`: Add backward-looking `causal_chain` JSON to each theme dict with `change` fields in impacts.

**Task 2: Frontend — Update API client**
- `frontend/src/api/client.js`: Update `searchMemory()` to accept `{ q, from, to }` params.

**Task 3: Frontend — MemoryResultCard component**
- New `frontend/src/components/MemoryResultCard.jsx`: Compact card with theme name, TemperatureBadge, date range, peak temp, article count. Purple left border when selected. Follows ThemeFeedCard pattern.

**Task 4: Frontend — Rework ThemeFeed for Memory tab**
- `frontend/src/components/ThemeFeed.jsx`: When Memory tab active, show search bar + quick filter chips + date range inputs + MemoryResultCard list. Debounced search. Quick chip click sets query. Reports `activeTab` and `selectedMemoryTheme` up to parent.

**Task 5: Frontend — CausalChain historical mode**
- `frontend/src/components/CausalChain.jsx`: Add `historical` prop. When true: "What Happened" header, "Outcome" label, direction shows `change` value instead of Bullish/Bearish.

**Task 6: Frontend — MemoryDetailPanel**
- New `frontend/src/components/MemoryDetailPanel.jsx`: Mirrors ThemeDetailPanel layout. Banner + tags + two columns (articles left, causal chain right). Uses `<CausalChain historical={true}>`. Shows "Select a historical theme" empty state.

**Task 7: Frontend — DashboardPage layout swap**
- `frontend/src/pages/DashboardPage.jsx`: Track `activeTab` state. Pass to ThemeFeed. When memory tab + selectedMemoryTheme, render MemoryDetailPanel instead of ThemeDetailPanel.

**Task 8: Frontend — HistoricalParallel component**
- New `frontend/src/components/HistoricalParallel.jsx`: Purple accent section below CausalChain. Calls `searchMemory(theme.name)`, filters self, shows first match. Dashed top border, "H" icon badge, purple-tinted card with link.

**Task 9: Frontend — Wire HistoricalParallel into detail views**
- `frontend/src/components/ThemeDetailPanel.jsx`: Add HistoricalParallel below CausalChain.
- `frontend/src/pages/ThemeDetailPage.jsx`: Add HistoricalParallel below CausalChain.

### Acceptance Criteria

**Given** the Memory Search tab is clicked
**When** the Memory Search view renders
**Then** a search input, quick filter chips, and optional date range are displayed

**Given** a user types a keyword (min 2 chars)
**When** 300ms debounce elapses
**Then** results from /api/memory/search are shown as compact cards in the left column

**Given** a user clicks a memory result card
**When** the card is selected
**Then** the right panel shows full detail (banner, tags, articles, backward-looking causal chain with "What Happened" + "Outcome")

**Given** a live theme has a causal chain
**When** the detail panel renders
**Then** a HistoricalParallel section appears below the CausalChain if a matching historical theme exists

**Given** no search results match
**When** results are empty
**Then** show "No matching historical themes found" with keyword suggestions

## Additional Context

### Dependencies

- No new npm packages needed (native debounce, native input type="month")
- No new Python packages needed
- Backend memory search API already exists and is functional

### Testing Strategy

- Manual browser testing: tab switching, search, result selection, detail rendering
- Verify backward-looking causal chains display correctly with past tense and percentages
- Verify HistoricalParallel appears on live themes with matching historical data
- Test empty states, no results, debounce behavior
- Test date range filtering on backend

### Notes

- Design reference: `_bmad-output/planning-artifacts/ux-design-final-mockup.html` (click "Memory Search" tab)
- Purple accent color for historical elements: #8b5cf6
- Outcome grid uses actual % changes instead of Bullish/Bearish
- Memory Search tab state preserved when switching back to Live Themes
