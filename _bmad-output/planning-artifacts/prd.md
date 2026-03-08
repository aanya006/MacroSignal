---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
inputDocuments:
  - 'fintech hacakthon notes- Google Docs.pdf'
  - 'NFC Hackathon Seeding Round .pdf'
workflowType: 'prd'
documentCounts:
  briefs: 0
  research: 2
  brainstorming: 0
  projectDocs: 0
classification:
  projectType: web_app
  domain: fintech
  complexity: high
  projectContext: greenfield
---

# Product Requirements Document - FinTech_Hackathon

**Author:** Aanya
**Date:** 2026-03-08

## Executive Summary

Asset managers in Singapore are drowning in signal noise — macroeconomic releases, central bank commentary, geopolitical developments, and sector events are fragmented across dozens of platforms, research notes, and internal channels. The critical pain: market-moving developments get buried, and by the time they surface, the opportunity (or risk) has already moved prices. Global AUM is rising toward $200 trillion by 2030, yet industry profit margins are shrinking — managers must do more with less, making tools that save time and improve decision quality essential.

This product is an AI-powered macro intelligence dashboard built for Singapore-based asset managers. It ingests real-time news and market data, clusters it into macro themes (e.g. "US Inflation", "China Tariffs", "MAS Policy"), scores each theme as Hot/Warm/Cool based on article frequency and recency, and tracks how themes evolve over time. Critically, it goes beyond what happened to explain *why it matters* — using LLM-powered causal chain reasoning to generate actionable intelligence in plain language (e.g. "Fed rate pause → dollar weakening → EM currencies strengthening → opportunity in EM bonds"). A built-in institutional memory layer ensures that past macro patterns and their outcomes are never lost, even as team members rotate.

### What Makes This Special

- **Causal Chain Intelligence:** No existing tool provides structured Trigger → Mechanism → Asset Impact reasoning in plain language. Bloomberg and AlphaSense show data; this product interprets it like a macro strategist.
- **Institutional Memory:** A searchable archive of every macro theme ever detected — how it evolved, how it resolved, and what happened in markets. When a pattern recurs, the system surfaces "this happened before — here's what followed." No competitor does this simply.
- **Singapore/Asia Regional Focus:** Tailored for the Singapore market — MAS policy announcements, SGD movements, STI trends, ASEAN trade dynamics, and Asia-specific macro signals that global trackers either miss entirely or gate behind $25k/year terminal fees.
- **Affordable Mid-Market Access:** Serious macro intelligence tools are priced for bulge-bracket institutions. This product targets mid-size asset managers in Asia and emerging markets who are currently underserved.

## Project Classification

- **Project Type:** Web Application (SPA dashboard with real-time data, interactive visualizations)
- **Domain:** FinTech (macro intelligence for investment/asset management)
- **Complexity:** High (real-time data aggregation, NLP/ML theme clustering, LLM integration, financial domain expertise)
- **Project Context:** Greenfield (new product for NTU FinTech Innovator's Hackathon 2026, seeding round deadline 11 Mar)

## Success Criteria

### User Success

- An asset manager can open the dashboard and within 30 seconds identify the top 3 macro themes affecting markets today
- Hot/Warm/Cool scoring is immediately intuitive — no explanation needed to understand which themes demand attention
- Causal chain panel delivers the "aha" moment: user sees not just "US Inflation is hot" but "Higher inflation → likely Fed hike → SGD strengthening → Singapore export pressure" and thinks "I need this"
- Theme history search returns relevant past patterns in under 2 clicks — "show me the last time MAS tightened policy"

### Business Success

- **Hackathon:** Score highly across all 5 judging criteria (Innovation, Technology/Prototype, UX, Feasibility/Impact, Market Potential — each 20%)
- **Portfolio/Resume value:** A polished, deployable prototype with clean code, clear architecture, and a compelling demo video that demonstrates real technical skill
- **Learning outcomes:** Team gains hands-on experience with LLM integration (Claude API), real-time data pipelines, NLP theme clustering, and full-stack web development

### Technical Success

- Live news data flowing through the pipeline — not mocked or hardcoded
- Theme clustering produces coherent, recognizable macro themes from raw news articles
- Hot/Cool scoring updates reflect actual changes in news volume and recency
- Claude API causal chain generation returns structured, plausible Trigger → Mechanism → Asset Impact reasoning
- Dashboard loads and renders theme feed within 3 seconds
- System works end-to-end as a demo: ingest → cluster → score → display → explain

### Measurable Outcomes

- Prototype demonstrates all 5 required features from the problem statement (theme tracking, hot/cool detection, cross-region connections, institutional memory, intuitive dashboard)
- Bonus feature (risk implication / causal chain reasoning) is functional and demo-ready
- Seeding round submission (GitHub repo + 5-min video pitch + project description) completed by 11 Mar 9am
- Codebase is clean, documented, and portfolio-ready (README, architecture docs, clear commit history)

## Product Scope

### MVP - Hackathon Prototype (by 11 Mar)

- **News Ingestion:** Pull articles from free news APIs (NewsAPI free tier, Google News RSS, or GDELT) focused on macro/financial news
- **Theme Clustering:** Group articles into macro themes using NLP (keyword-based or lightweight LLM classification)
- **Hot/Cool Scoring:** Score themes based on article count + recency, display with color-coded badges
- **Theme Feed Dashboard:** Main view showing today's themes with scores, article cards (title, source, date, AI summary), and source links
- **Interactive Date Timeline:** Selectable date-based timeline per theme showing the last 30 days only — users click dates to filter articles, with fast-scroll animation on date change. Default shows most recent articles.
- **Cross-Region/Asset Tags:** Tag themes with affected regions (US, EU, Asia/Singapore) and asset classes (Equities, Bonds, FX, Commodities)
- **Causal Chain Panel:** Claude API generates "Trigger → Mechanism → Asset Impact" for each hot theme
- **Singapore/Asia Focus:** Priority ingestion of MAS, SGX, ASEAN-related news sources
- **Institutional Memory:** Searchable archive of past themes with articles and outcomes, pre-seeded with historical data

### Growth Features (Post-MVP, if time permits)

- **Morning Briefing Summary:** AI-generated overnight macro summary at top of dashboard
- **Alert System:** Notifications when a theme changes trend status
- **Customizable Watchlists:** Users can favorite themes or filter by region/asset class
- **Theme Bookmarking:** Save themes for later review

### Vision (Portfolio showcase)

- Clean GitHub repo with comprehensive README, architecture diagram, and setup instructions
- Demo video that tells a compelling story from problem → solution → impact
- Public deployment for portfolio demonstration
- Reusable as a portfolio piece demonstrating: LLM integration, real-time data processing, financial domain knowledge, full-stack development

## User Journeys

### Journey 1: Rachel Tan — Portfolio Manager, Morning Macro Briefing (Primary - Success Path)

**Persona:** Rachel Tan, 38, Senior Portfolio Manager at a mid-size asset management firm in Singapore. Manages a $500M multi-asset portfolio spanning Asian equities, EM bonds, and FX. She's experienced but time-poor — back-to-back client meetings from 10am, so her morning window (7:30-9:30am) is when all macro analysis happens. Currently relies on Bloomberg terminal, 3 WhatsApp groups, and a junior analyst's email summary that's often incomplete.

**Opening Scene:** It's 7:45am. Rachel sits down with coffee at her desk at Raffles Place. Overnight, the Fed released hawkish minutes, China posted weak PMI data, and MAS issued a statement on SGD policy. She knows *something* happened but doesn't know what matters. On a normal day, she'd spend 45 minutes scanning Bloomberg, Reuters, and CNA to piece it together.

**Rising Action:** Rachel opens the macro intelligence dashboard. The **Theme Feed** shows today's macro themes ranked by temperature:
- "Fed Policy Trajectory" — Hot
- "China Manufacturing Slowdown" — Warm
- "MAS Monetary Policy" — Hot
- "Japan Yield Curve Control" — Cool

She taps "MAS Monetary Policy" (Hot). She sees 4 linked articles (CNA, Business Times, MAS official statement, Reuters), each with a one-line AI summary. Below, the **Date Timeline** highlights key dates — she clicks through recent dates and the articles fast-scroll into view, showing MAS-related coverage spiking over the past 5 days.

**Climax:** Rachel scrolls to the **Causal Chain Panel**: *"MAS reaffirms tight SGD NEER band → SGD appreciation continues → Singapore export sector earnings pressure → STI industrials underperformance likely."* In 3 minutes, she has a structured view of what happened, why it matters for key asset classes, and can decide how to act. This would have taken her 45 minutes to piece together manually.

**Resolution:** By 8:15am — 30 minutes earlier than usual — Rachel has her macro view locked in. She flags the MAS theme to revisit after her 10am meeting, glances at the cross-region tags to confirm the China slowdown is tagged to "Asia, Commodities, EM Bonds," and heads to her first meeting confident she hasn't missed anything overnight.

### Journey 2: David Lim — Junior Analyst, Research Deep Dive (Primary - Edge Case)

**Persona:** David Lim, 24, Junior Research Analyst at the same firm. 18 months into his career. His job is to prepare macro briefing notes for Rachel and the investment committee. Smart but still building domain intuition — he knows the data but sometimes misses the second-order connections. Currently spends 2-3 hours daily manually compiling news summaries from multiple sources.

**Opening Scene:** David gets a Slack message from Rachel: "IC meeting moved to 2pm — I need a briefing note on the China slowdown theme and how it connects to our ASEAN exposure. Can you pull something together?" David normally dreads this — it means hours of searching, reading, and trying to connect dots across regions.

**Rising Action:** David opens the dashboard and searches "China Manufacturing" in the theme feed. He finds the theme with its full article trail — 12 articles over the past week, with AI summaries for each. He doesn't need to read all 12; the summaries tell him which 3 are most relevant. He clicks through to the **Cross-Region/Asset Tags** and sees the theme is tagged: "Asia, Commodities, Equities, FX" with connections to "ASEAN Trade" and "Commodity Prices" themes.

**Climax:** David opens the **Causal Chain Panel** for the China theme: *"China PMI contraction → reduced commodity demand → commodity price decline → ASEAN export revenue pressure → SGD/MYR/THB weakening against USD."* He immediately sees the ASEAN connection Rachel asked about — laid out in a causal chain he can directly reference. He clicks the **Theme Timeline** and sees this theme has been warming for 3 weeks, validating it's not a one-day blip. He checks the institutional memory: *"Similar pattern: China PMI contraction in Q2 2024 → ASEAN currencies weakened 3-5% over following 6 weeks."*

**Resolution:** In 40 minutes instead of 2.5 hours, David has a briefing note with sourced articles, a causal chain, historical context, and cross-asset implications. The note is stronger than anything he's produced before because the tool helped him see connections he would have missed. Rachel is impressed at the IC meeting. David's confidence grows — the tool doesn't replace his analysis, it accelerates his learning curve.

### Journey 3: Aanya (Dev Team) — System Admin, Data Pipeline Monitoring (Admin/Ops)

**Persona:** Aanya, developer and system administrator for the hackathon prototype. Responsible for ensuring news ingestion runs smoothly, API rate limits aren't exceeded, and the clustering pipeline produces quality output.

**Opening Scene:** It's the morning of the hackathon demo. Aanya needs to verify the system is pulling live data and the dashboard is rendering correctly.

**Rising Action:** Aanya checks the system status: news API calls are returning 200s, the last ingestion cycle pulled 47 articles, theme clustering grouped them into 8 themes. She notices one theme — "Global Oil Markets" — has only 1 article, which suggests a clustering edge case. She flags it for review.

**Climax:** Aanya verifies the Claude API causal chain generation is working by spot-checking 2 hot themes. The responses are coherent and well-structured. The dashboard loads in under 2 seconds. Everything is demo-ready.

**Resolution:** System is healthy, data is flowing, and the prototype is ready for the judges. Aanya can focus on the pitch rather than firefighting.

### Journey Requirements Summary

| Journey | Capabilities Revealed |
|---|---|
| Rachel (PM - Morning Macro Review) | Theme feed with hot/cool ranking, article cards with AI summaries, interactive date timeline (last 30 days), causal chain panel, cross-region/asset tags, theme bookmarking |
| David (Analyst - Deep Dive) | Theme search, article trail with summaries, cross-region connections, causal chain reasoning, interactive date timeline (last 30 days), institutional memory / historical pattern lookup |
| Aanya (Admin - Monitoring) | System health dashboard (stretch), API status monitoring, ingestion cycle logs, clustering quality review |

**Key capabilities across all journeys:**
- Theme feed ranked by hot/cool score
- Article cards with source links and AI summaries
- Interactive date timeline (last 30 days, with epicenter heat visualization)
- Causal chain panel (Trigger → Mechanism → Asset Impact)
- Cross-region and cross-asset tagging
- Theme search and filtering
- Institutional memory / historical pattern matching

## Domain-Specific Requirements

### Compliance & Regulatory

- **Financial Disclaimer:** All AI-generated causal chains and risk implications must display a clear "For informational purposes only — not financial advice" disclaimer. Judges will expect this for a fintech product.
- **News API Terms of Service:** Comply with attribution requirements for free-tier news APIs (e.g. NewsAPI requires source attribution on displayed articles). Build attribution into article card components from day one.
- **Data Accuracy:** AI-generated summaries and causal chains must be clearly labeled as AI-generated content, not presented as factual analysis.

### Technical Constraints

- **API Rate Limits:** Free-tier news APIs typically cap at 100-500 requests/day. Architecture must batch and cache aggressively — Redis is well-suited for this.
- **Claude API Costs:** Causal chain generation should be triggered selectively (hot themes only, not every theme) to manage token usage. Cache Claude responses in Redis to avoid regenerating for the same theme within a time window.
- **No PII Handling:** Product ingests only public news data — no user financial data, no portfolio information, no authentication/login needed for the prototype. This significantly reduces security scope.

### Integration Requirements

- **News Data Sources:** Free-tier APIs (NewsAPI, GDELT, Google News RSS). Must handle API failures gracefully — if a source is down, dashboard still renders with cached data.
- **Claude API:** Anthropic SDK (Python) for causal chain generation. Structured prompts returning Trigger → Mechanism → Asset Impact format.
- **Tech Stack:**
  - **Frontend:** React (SPA dashboard)
  - **Backend:** Python (API server, news ingestion, theme clustering)
  - **Database:** PostgreSQL (articles, themes, historical data, institutional memory)
  - **Cache:** Redis (API response caching, rate limit management, hot/cool scores)

### Risk Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| News API rate limit exceeded | No new data flowing | Batch ingestion on schedule (e.g. every 30 min), cache all responses in Redis, serve from cache when API unavailable |
| Claude API latency/cost | Slow causal chain generation, budget overrun | Pre-generate for hot themes only, cache responses, set daily token budget |
| Theme clustering produces incoherent themes | Poor demo quality | Use keyword-based clustering as fallback, manually seed initial theme categories for Singapore/Asia macro topics |
| Free API data quality is low | Themes based on irrelevant articles | Filter by financial/macro keywords before clustering, prioritize reputable sources (Reuters, CNA, Business Times) |

## Innovation & Novel Patterns

### Detected Innovation Areas

1. **Causal Chain Intelligence (Primary Innovation):** Existing macro tools (Bloomberg, AlphaSense, Dataminr) show what happened. This product uses LLM reasoning to generate structured causal chains: Trigger → Mechanism → Asset Impact. This transforms raw news into actionable macro intelligence — a capability that only became possible with the emergence of capable LLMs like Claude. No competitor offers this as a standalone, accessible feature.

2. **Temperature-Scored Theme Intelligence:** While trending topic detection exists, no tool combines article frequency + recency into a simple Hot/Warm/Cool temperature badge that an asset manager can glance at and immediately prioritize. The simplicity is the innovation — reducing complex signal analysis to a traffic-light metaphor.

3. **Accessible Institutional Memory:** Enterprise knowledge management exists (Confluence, Notion), but no tool automatically builds a searchable archive of macro themes with their evolution and resolution. When a pattern recurs (e.g. "MAS tightening cycle"), the system surfaces historical context automatically. This solves the real problem of institutional knowledge loss when analysts leave or time passes.

4. **Democratized Macro Intelligence:** Serious macro tools are priced at $25k+/year (Bloomberg Terminal) and designed for quantitative analysts. This product makes macro intelligence accessible to mid-market asset managers and junior analysts who lack both the budget and the quantitative background — using natural language instead of complex dashboards.

### Market Context & Competitive Landscape

| Competitor | What They Do | What They Don't Do |
|---|---|---|
| Bloomberg Terminal | Comprehensive market data, topic frequency tracking | No plain-language causal reasoning, $25k/year, complex UI |
| AlphaSense | AI-powered document search, trending topics | No hot/cool scoring, no causal chains, enterprise pricing |
| Dataminr | Real-time event detection, alerts | News alerts only, no theme evolution tracking, no memory |
| Permutable AI | Cross-asset AI signals | Complex, expensive, no accessible temperature scoring |
| Google News / RSS | Free news aggregation | No financial context, no clustering, no intelligence layer |

**White space this product occupies:** Affordable, LLM-native macro intelligence with causal reasoning and institutional memory, focused on Singapore/Asia mid-market asset managers.

### Validation Approach

- **Hackathon Demo:** End-to-end prototype demonstrating live news → theme clustering → hot/cool scoring → causal chain generation. Judges can interact with real data and see the causal reasoning in action.
- **Quality Benchmark:** Compare Claude-generated causal chains against actual market analyst reports for the same events — do they reach similar conclusions?
- **User Comprehension Test:** Can a non-finance judge understand the causal chain panel within 10 seconds? If yes, the accessibility innovation is validated.

### Risk Mitigation

| Innovation Risk | Fallback |
|---|---|
| Claude causal chains are inaccurate or generic | Pre-craft prompt templates with Singapore/Asia financial context; include few-shot examples of good causal chains |
| Theme clustering produces noise instead of signal | Seed with predefined macro theme categories (Fed Policy, MAS Policy, China Economy, etc.) and use keyword matching as baseline |
| Hot/Cool scoring doesn't reflect real market attention | Calibrate scoring weights with known events (e.g. a Fed rate decision should always score Hot) |
| Institutional memory has no historical data at launch | Pre-seed database with 2-3 months of historical themes from archived news to demonstrate the memory feature |

## Web Application Specific Requirements

### Project-Type Overview

Single Page Application (SPA) built with React, serving as a macro intelligence dashboard. The application is a data-heavy, read-oriented tool — users consume AI-processed information rather than creating content. The primary interaction pattern is: scan briefing → explore themes → drill into causal chains → reference source articles.

### Technical Architecture Considerations

**Application Architecture:**
- **SPA (React):** Client-side routing, component-based UI, state management for theme data and user interactions
- **API-Driven:** React frontend consumes a Python REST API backend. Clear separation of concerns — frontend handles presentation, backend handles data processing and LLM integration
- **Batch Data Model:** News ingestion runs on a scheduled cycle (every 30 min). Dashboard serves pre-processed data from PostgreSQL/Redis cache. No WebSocket or real-time push needed for the prototype.

**Browser Support:**
- Chrome (latest) — primary and only target for hackathon demo
- No cross-browser testing required. Focus development time on features, not compatibility.

**Responsive Design:**
- Desktop-first design — asset managers use this at their desk on monitors
- Minimum viewport: 1280px width
- Mobile responsiveness is not required for the prototype

**Performance Targets:**
- Initial dashboard load: < 3 seconds
- Theme detail view (click to expand): < 1 second
- Causal chain generation display: < 2 seconds (served from cache; Claude API pre-generates)
- Article card rendering: instant (data pre-fetched with theme)

**SEO:** Not applicable — this is a dashboard tool, not a public content site.

**Accessibility:** Basic best practices — semantic HTML, sufficient color contrast for hot/warming/cool badges, keyboard-navigable theme list. No formal WCAG compliance target for hackathon.

### Frontend Component Architecture

| Component | Purpose | Data Source |
|---|---|---|
| Morning Briefing Panel (Post-MVP) | AI-generated summary of overnight macro developments | Backend API → Claude-generated, cached in Redis |
| Theme Feed | Scrollable list of macro themes with hot/cool badges | Backend API → PostgreSQL themes table |
| Theme Detail View | Expanded view with articles, timeline, causal chain | Backend API → articles + Claude causal chain |
| Article Cards | Title, source, date, AI summary, source link | Backend API → PostgreSQL articles table |
| Date Timeline | Interactive date navigation — users select dates to filter articles with fast-scroll animation | Backend API → article published_at dates |
| Causal Chain Panel | Trigger → Mechanism → Asset Impact display | Backend API → Claude-generated, cached |
| Cross-Region/Asset Tags | Color-coded region and asset class badges | Backend API → theme metadata |
| Theme Search | Search/filter themes by keyword | Client-side filtering on loaded theme data |

### Implementation Considerations

- **State Management:** React Context or lightweight state library (Zustand) — Redux is overkill for this scope
- **Charting:** Lightweight library for theme timeline (Recharts or Chart.js — both free, React-friendly)
- **Styling:** CSS Modules or Tailwind CSS for rapid UI development
- **API Client:** Fetch API or Axios for backend communication
- **Deployment:** Docker Compose for local development and production. Deployed on AWS EC2 with Cloudflare DNS/CDN for the hackathon demo. Live URL required for submission.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving MVP — demonstrate the complete intelligence pipeline end-to-end with real data. Every feature in MVP must contribute to the hackathon demo narrative: "watch live news become actionable macro intelligence in seconds."

**Resource Requirements:**
- Aanya: Frontend (React dashboard, all UI components)
- Akul + Saanvi: Backend (Python API, news ingestion, theme clustering, Claude integration, PostgreSQL/Redis setup)
- Timeline: 3 days (8 Mar → 11 Mar 9am submission)

### MVP Feature Set (Phase 1 — Hackathon Prototype)

**Core User Journeys Supported:**
- Rachel (PM) — partial: theme feed, article cards, causal chain, cross-region tags (no morning briefing)
- David (Analyst) — full: theme search, article trail, causal chain, theme timeline, institutional memory

**Must-Have Capabilities:**

| # | Feature | Justification |
|---|---|---|
| 1 | News Ingestion Pipeline | Foundation — without data, nothing works. Batch pull from free APIs every 30 min, filtered for financial/macro keywords |
| 2 | Theme Clustering | Core differentiator pipeline. Group articles into recognizable macro themes. **Highest technical risk — prioritize early.** |
| 3 | Hot/Warm/Cool Scoring | Required by problem statement. Score based on article count + recency. Visual badges on theme feed. |
| 4 | Theme Feed Dashboard | Primary UI. Scrollable list of themes ranked by temperature with article cards (title, source, date, AI summary, source link) |
| 5 | Interactive Date Timeline | Required by problem statement. Selectable date navigation per theme showing last 30 days only — click dates to filter articles with fast-scroll animation, default to most recent |
| 6 | Cross-Region/Asset Tags | Required by problem statement. Tag themes with regions (US, EU, Asia/Singapore) and asset classes (Equities, Bonds, FX, Commodities) |
| 7 | Causal Chain Panel | Primary innovation. Claude API generates Trigger → Mechanism → per-asset-class impacts (Equities, Bonds, FX, Commodities) for hot themes. Asset impacts shown as a 2x2 grid with directional indicators (Bullish/Bearish/Neutral). Cache in Redis. |
| 8 | Institutional Memory | Key differentiator. Searchable archive of past themes with articles and outcomes. Pre-seed with historical data to demonstrate value at demo. |
| 9 | Theme Search | Required by problem statement. Filter/search themes by keyword |
| 10 | Financial Disclaimer | "For informational purposes only" on all AI-generated content |
| 11 | Docker & Deployment | Docker Compose for cross-platform dev (Mac/Windows/Linux). AWS EC2 deployment with Cloudflare DNS/CDN. Live URL for hackathon submission. |

**Build Order (risk-first):**
1. News ingestion + theme clustering (highest risk, backend — Akul/Saanvi, days 1-2)
2. PostgreSQL schema + Redis caching (backend — Akul/Saanvi, day 1)
3. Dashboard shell + theme feed UI (frontend — Aanya, days 1-2)
4. Hot/cool scoring + cross-region tagging (backend — Akul/Saanvi, day 2)
5. Claude causal chain integration (backend — Akul/Saanvi, day 2)
6. Theme timeline chart + article cards (frontend — Aanya, day 2)
7. Causal chain panel + institutional memory UI (frontend — Aanya, day 2-3)
8. Institutional memory backend + pre-seeded data (backend — day 2-3)
9. Docker Compose setup + AWS EC2 deployment + Cloudflare DNS (all, day 2-3)
10. Integration testing + demo prep (all, day 3)
11. Video pitch recording + GitHub README (all, day 3)

### Post-MVP Features (Phase 2 — If Time Permits)

- **Morning Briefing Summary:** AI-generated overnight macro summary at top of dashboard
- **Alert System:** Notifications when a theme changes trend status
- **Customizable Watchlists:** Favorite themes, filter by region/asset class
- **Theme Bookmarking:** Save themes for later review

### Vision Features (Phase 3 — Portfolio Showcase)

- Extended historical data coverage
- Multi-user support with personalized focus areas

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Theme clustering produces incoherent results | High | Critical — breaks the entire product narrative | **De-risk first.** Start with predefined theme categories (Fed Policy, MAS Policy, China Economy, ASEAN Trade, Oil/Commodities, etc.) and use keyword matching as baseline. Layer NLP clustering on top only if time permits. This guarantees coherent themes for the demo. |
| Claude API causal chains are generic/unhelpful | Medium | High — weakens primary differentiator | Pre-craft detailed prompt templates with Singapore/Asia financial context. Include 2-3 few-shot examples of good causal chains. Test and iterate prompts early (day 1-2). |
| Free news API data is insufficient | Medium | High — empty dashboard at demo | Identify 2-3 backup data sources. Pre-seed database with recent articles as safety net. Test API reliability on day 1. |
| Redis/PostgreSQL setup issues | Low | Medium — slows development | Use Docker Compose for local dev and production. Keep schema simple — can always add indexes later. |
| AWS deployment fails or is slow | Medium | High — no live demo URL | Docker Compose makes deployment identical to local. Single EC2 instance, one `docker-compose up -d`. Test deployment on day 2, not day 3. |

**Market Risks:**
- Hackathon judges may not understand the financial domain deeply. Mitigation: causal chains must be written in plain language, not jargon. The demo video must clearly explain the problem before showing the solution.

**Resource Risks:**
- 3 days is tight for 3 people. Mitigation: strict MVP boundaries — no scope creep. If theme clustering takes longer than expected, fall back to keyword-based predefined categories immediately rather than debugging NLP. Ship a working demo over a perfect one.

## Functional Requirements

### News Data Ingestion

- FR1: System can ingest news articles from multiple free-tier news APIs on a scheduled batch cycle
- FR2: System can filter ingested articles by financial and macroeconomic keywords before processing
- FR3: System can prioritize Singapore/Asia-focused news sources (MAS, CNA, Business Times, Reuters Asia)
- FR4: System can store ingested articles with metadata (title, source, date, URL, full text) in the database
- FR5: System can serve cached data when a news API source is unavailable

### Theme Intelligence

- FR6: System can cluster ingested articles into recognizable macro themes (e.g. "Fed Policy", "MAS Monetary Policy", "China Manufacturing")
- FR7: System can assign a Hot/Warm/Cool temperature score to each theme based on article count and recency
- FR8: System can tag each theme with affected regions (US, EU, Asia/Singapore) and asset classes (Equities, Bonds, FX, Commodities)
- FR9: System can track theme article dates within a rolling 30-day window to support the interactive date timeline
- FR10: System can update theme scores and clustering on each ingestion cycle

### Causal Chain Reasoning

- FR11: System can generate a structured causal chain (Trigger → Mechanism → per-asset-class impacts for Equities, Bonds, FX, Commodities with directional indicators) for each hot theme using Claude API
- FR12: System can cache generated causal chains to avoid redundant API calls for the same theme within a time window
- FR13: System can display causal chains in plain language accessible to non-quantitative users
- FR14: System can label all AI-generated causal chains with an "AI-generated — not financial advice" disclaimer

### Institutional Memory

- FR15: System can store all detected themes and their associated articles as historical records
- FR16: Asset manager can search historical themes by keyword (e.g. "MAS tightening", "inflation 2024")
- FR17: System can surface historical theme context when a similar pattern recurs (e.g. "this theme appeared before — here's what happened")
- FR18: System can display pre-seeded historical data to demonstrate institutional memory at launch

### Dashboard & Navigation

- FR19: Asset manager can view a theme feed ranked by hot/cool score as the primary dashboard view
- FR20: Asset manager can click on a theme to view its detail page with articles, timeline, causal chain, and tags
- FR21: Asset manager can view article cards showing title, source name, date, and one-line AI summary for each article in a theme
- FR22: Asset manager can click an article card to navigate to the original source article
- FR23: Asset manager can navigate an interactive date timeline (last 30 days only) to filter articles by date, with fast-scroll animation on date selection and most recent articles shown by default
- FR24: Asset manager can search and filter themes by keyword from the dashboard
- FR25: Asset manager can view cross-region and cross-asset tags on each theme as color-coded badges

### Article Intelligence

- FR26: System can generate a one-line AI summary for each ingested article
- FR27: System can attribute each article to its original source in compliance with API terms of service
- FR28: System can display article publication date and source name alongside each article card

### System Operations

- FR29: System can run news ingestion on an automated schedule (every 30 minutes)
- FR30: System can handle API rate limits gracefully without crashing or losing data
- FR31: System can serve the dashboard from pre-processed cached data for fast load times

## Non-Functional Requirements

### Performance

- NFR1: Dashboard initial load completes within 3 seconds serving pre-cached theme data
- NFR2: Theme detail view (click to expand) renders within 1 second
- NFR3: Causal chain panel displays within 2 seconds (served from Redis cache, not generated on-demand)
- NFR4: Theme search/filter returns results within 500ms (client-side filtering on loaded data)
- NFR5: News ingestion batch cycle completes within 60 seconds per run

### Security

- NFR6: All API keys (news APIs, Claude API) are stored as environment variables, never committed to the repository
- NFR7: Backend API does not expose raw API keys or internal system details to the frontend
- NFR8: No user authentication required for the hackathon prototype — the dashboard is open access

### Integration

- NFR9: System gracefully handles news API failures — dashboard continues to serve cached data with a "last updated" timestamp
- NFR10: System respects news API rate limits — batch scheduling prevents exceeding free-tier quotas
- NFR11: Claude API calls include timeout handling — if Claude is slow or unavailable, dashboard renders without causal chains rather than hanging
- NFR12: All external API dependencies have fallback behavior — no single API failure should crash the application

### Data Quality

- NFR13: Theme clustering produces at minimum 5 and at most 15 distinct themes per ingestion cycle to avoid noise or over-consolidation
- NFR14: AI-generated article summaries are limited to one sentence (max 30 words) for scannability
- NFR15: Causal chains follow the consistent Trigger → Mechanism → Asset Impact format across all themes
