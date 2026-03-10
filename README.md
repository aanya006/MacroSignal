# MacroSignal

**AI-powered macro intelligence for asset managers.**

Bloomberg Terminal costs $25,000/year and doesn't tell you *why* something matters. AlphaSense has no momentum scoring. No tool on the market combines theme tracking, causal chain reasoning, and institutional memory in a single product.

MacroSignal does.

---

## Architecture Overview

This README covers the technical implementation — architecture, API reference, deployment, and scaling strategy. For a concise product summary, see [PROJECT_DESCRIPTION.md](./PROJECT_DESCRIPTION.md).

---

## How It Solves the Problem Statement

| Requirement | How MacroSignal Addresses It |
|---|---|
| Track how a topic evolves over time | Interactive 30-day date timeline per theme showing article volume heatmap |
| Identify when a theme becomes "hot" or "cool" | Exponential decay temperature scoring (24hr half-life) with Hot / Warm / Cool badges |
| Connect developments across regions and asset classes | Region + asset class tagging aggregated to theme level; Market Signals swimlane for cross-asset view |
| Maintain institutional memory of past discussions | Searchable Precedents archive with date, category, and keyword filters |
| Provide intuitive dashboard with source article navigation | Three-panel SPA: Watch List → Theme Detail (articles + causal chain) + Precedents tab |
| (Bonus) Propose risk implications per macro theme | Claude-generated Trigger → Mechanism → Asset Impacts for Equities, Bonds, FX, Commodities |

---

## Key Features

### Live Watch List
Macro themes ranked by temperature score. Hot and Warm themes surface first. Cool themes collapse to reduce noise. Themes span US policy, China economic dynamics, MAS/SGD management, OPEC+, AI infrastructure, and more — with Singapore-specific coverage as a core differentiator.

### Temperature Scoring
Scores are computed using exponential decay with a 24-hour half-life:

```
score = Σ exp(-ln(2)/24 × age_hours)  for articles in last 7 days

Hot   ≥ 3.0  (3+ fresh articles in the last 24h equivalent)
Warm  ≥ 1.0
Cool  < 1.0
```

This captures momentum, not just volume — a theme with 10 articles from 6 days ago scores lower than one with 3 articles from this morning.

### Causal Chain Intelligence
For each Hot theme, Claude generates a structured causal reasoning chain:

```
Trigger → Mechanism → Asset Impacts (Equities / Bonds / FX / Commodities)
```

Example: *"Fed signals pause → dollar weakening → EM currencies strengthen → opportunity in EM bonds"*

This is the core differentiator vs. Bloomberg/AlphaSense: tools give data, MacroSignal gives reasoning.

### Institutional Memory (Precedents)
A searchable archive of historical themes with full causal chains and article timelines. Users can search by keyword, date range, or crisis type (Currency & FX, Equity Crash, Policy Shock, Trade & Geopolitical, Debt & Credit). When viewing a live theme, the system auto-surfaces the closest historical parallel — so a current tariff escalation automatically links to past trade war precedents.

### Market Signals
Articles that don't fit the tracked macro themes are surfaced in asset-class swimlanes (Equities, Bonds, FX, Commodities, Crypto, Real Estate) so no financial news is discarded.

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| Vite | 7 | Build tool |
| Tailwind CSS | v4 | Styling |
| Zustand | latest | State management |
| React Router | v7 | Client-side routing |
| Axios | latest | HTTP client |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Flask | latest | REST API framework |
| Gunicorn | latest | Production WSGI server |
| PostgreSQL | 16 | Primary database |
| Redis | 7 | Caching layer |
| Anthropic SDK | 0.84.0 | Claude AI integration |
| APScheduler | latest | Background ingestion (30-min cycle) |

### AI Models
| Model | Usage | Reason |
|---|---|---|
| Claude Sonnet 4.6 | Article classification + causal chain generation | Higher accuracy for nuanced financial classification and CFA-level causal reasoning |
| Claude Haiku | Article summarisation | Cost-efficient for high-frequency generation tasks |

### Infrastructure
- **Containerisation:** Docker Compose (4 containers: PostgreSQL, Redis, Flask backend, nginx frontend)
- **Deployment target:** AWS EC2 (t3.small) + Cloudflare DNS/CDN
- **Frontend:** Multi-stage Docker build — Vite → nginx serving static files + `/api/*` proxy to backend

---

## Architecture

```
News Sources (NewsAPI + Google RSS + 5 direct RSS feeds)
    │
    ▼
news_ingestion.py  ──── fetch, filter, OG image scrape, store to PostgreSQL
    │
    ▼
theme_classifier.py ─── Claude Sonnet 4.6 classifies article → theme slugs
    │                    (confidence < 0.5 → routed to Market Signals pool)
    ▼
causal_chain.py ──────── Claude Sonnet 4.6 generates Trigger → Mechanism → Impacts
    │                    (Hot themes only; 2hr Redis TTL)
    ▼
summariser.py ────────── Claude Haiku generates 30-word article summaries
    │                    (24hr Redis TTL)
    ▼
tagging.py ───────────── Regex region + asset class tagging
    │
    ▼
Redis Cache ──────────── 5-min TTL for theme list, 2hr for chains, 24hr for summaries
    │
    ▼
Flask REST API ───────── 7 endpoints served to React SPA
```

### Database Schema
```sql
themes        — macro themes with score_label, score_value, causal_chain (JSONB)
articles      — ingested articles with ai_summary, region_tags[], asset_tags[], theme_id FK
theme_history — daily snapshots for institutional memory
ingestion_logs — audit trail of all ingestion runs
```

### API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/themes` | All live themes ranked by score |
| GET | `/api/themes/<slug>` | Theme detail with causal chain |
| GET | `/api/themes/<slug>/articles` | Articles for theme (optional `?date=` filter) |
| GET | `/api/memory/search` | Historical theme search (`?q=`, `?from=`, `?to=`) |
| GET | `/api/signals` | Unthemed articles grouped by asset class |
| GET | `/api/status` | System health and last ingestion timestamp |
| POST | `/api/ingest` | Trigger manual ingestion |

---

## Scalability Architecture

The current deployment targets a single EC2 instance suitable for demonstration and pilot usage. The architecture is designed to scale horizontally with minimal changes:

| Layer | Current | Scale Path |
|---|---|---|
| Database | Single PostgreSQL 16 | AWS RDS with read replicas; partition `articles` table by `published_at` |
| Cache | Single Redis 7 | AWS ElastiCache Redis cluster |
| Backend | Single Gunicorn process | Multiple Flask workers behind an ALB; stateless by design |
| Frontend | nginx on EC2 | CloudFront CDN (already using Cloudflare DNS) |
| Ingestion | APScheduler in-process | Extract to AWS Lambda or a dedicated worker container |
| AI costs | Per-request Claude API | Batch classification during off-peak; fine-tune a smaller model on labelled data at scale |

The PostgreSQL connection pool and Redis cache layers mean the backend is stateless and can be horizontally scaled immediately without schema changes.

---

## Regulatory Positioning

MacroSignal is designed as an **information aggregation and research tool**, not an investment advisory service.

- All AI-generated causal chain outputs are clearly labelled as AI-generated and displayed with an explicit disclaimer: *"For informational purposes only. This content does not constitute investment advice, a solicitation, or a recommendation to buy or sell any financial instrument."*
- MacroSignal does not hold, manage, or execute any financial assets.
- Under Singapore's Securities and Futures Act (SFA) Cap. 289, the product does not trigger licensing requirements as a financial adviser or capital markets services licensee, as it provides general financial information aggregation rather than personalised investment recommendations.
- Institutional deployments would be subject to standard enterprise data agreements and internal compliance review by the client firm (e.g., as a research tool licensed to a registered fund manager).
- The AI disclaimer framework is designed to comply with MAS Notice on Technology Risk Management and aligns with MAS's principle-based approach to AI governance in financial services.

---

## Market Opportunity

### Problem Size
- Global AUM: $139 trillion today, projected $200 trillion by 2030 (PwC)
- Asset manager profit margins have fallen ~19% since 2018 and are projected to fall another 9% by 2030 — firms must do more with less
- Bloomberg Terminal: $25,000/user/year — accessible only to bulge-bracket institutions
- Mid-market asset managers in Singapore, Southeast Asia, India, and broader emerging markets are underserved by existing tools

### Target Segments
| Segment | Description | Willingness to Pay |
|---|---|---|
| Boutique asset managers | 5–50 person firms, AUM $100M–$2B | $200–500/user/month |
| Family offices | Single/multi-family offices managing private wealth | $300–800/user/month |
| Corporate treasury teams | MNCs monitoring macro risk for FX/hedging decisions | $500–1,500/team/month |
| Research analysts | Buy-side and sell-side research departments | $150–300/user/month |

### Competitive Landscape
| Tool | Price | Hot/Cool Scoring | Causal Chain Reasoning | Institutional Memory |
|---|---|---|---|---|
| Bloomberg Terminal | $25,000/yr | No | No | No |
| AlphaSense | $15,000+/yr | No | No | No |
| Permutable AI | Enterprise pricing | Partial | No | No |
| Dataminr | Enterprise pricing | Real-time alerts | No | No |
| **MacroSignal** | **$200–1,500/mo** | **Yes** | **Yes** | **Yes** |

### Revenue Model
**SaaS subscription** with per-seat pricing:
- **Starter** — $299/month per seat (up to 3 users): Live Watch List, Causal Chains, 30-day history
- **Professional** — $799/month per team (up to 10 users): All features + API access + custom theme requests
- **Enterprise** — Custom pricing: White-label, SSO, on-premise deployment, dedicated ingestion pipeline

**Unit economics at scale:** Claude API cost per causal chain generation is approximately $0.01–0.03 per theme per day. With 30-day refresh cycles, total AI inference cost per customer is well under $10/month, leaving strong gross margins at the Starter tier.

### Go-to-Market Strategy
1. **Pilot with Singapore-based boutique asset managers** via NTU alumni network and NTUpreneur ecosystem connections — target 5 design partners in Q2 2026
2. **Content-led SEO** — publish weekly macro theme summaries publicly to drive inbound from asset management research teams
3. **Channel partnerships** — integrate with SGX data partnerships and MAS FinTech regulatory sandbox for credibility
4. **Conference presence** — Singapore FinTech Festival, CFA Society Singapore events

### Long-term Moat
The institutional memory layer creates a **data flywheel**: every month the system runs, it accumulates more historical precedents that competitors cannot replicate overnight. A firm that has been using MacroSignal for 2 years has 2 years of proprietary, searchable institutional context — a Bloomberg subscription cannot substitute for that.

---

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- An Anthropic API key
- A NewsAPI key

### Quick Start
```bash
git clone <repo-url>
cd FinTech_Hackathon

# Copy environment template
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and NEWS_API_KEY in .env

# Start all services
docker compose up --build

# App is available at http://localhost:3000
# API is available at http://localhost:5000
```

### Environment Variables
```
ANTHROPIC_API_KEY=your_anthropic_key
NEWS_API_KEY=your_newsapi_key
POSTGRES_DB=macrosignal
POSTGRES_USER=macrosignal
POSTGRES_PASSWORD=your_password
REDIS_URL=redis://redis:6379/0
```

---

## Team

Built for the NTU FinTech Innovator's Hackathon 2026 by:

| Name | Role |
|---|---|
| Aanya | Frontend — React SPA, UI/UX design, component architecture |
| Akul | Backend — Flask API, news ingestion pipeline, database schema |
| Saanvi | Backend — AI integration, theme clustering, causal chain generation |

---

*MacroSignal is a research and information aggregation tool. All AI-generated content is for informational purposes only and does not constitute investment advice under the Securities and Futures Act (Cap. 289) of Singapore.*
