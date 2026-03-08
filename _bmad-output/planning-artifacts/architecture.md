---
stepsCompleted:
  - step-01-init
  - step-02-context
  - step-03-starter
  - step-04-decisions
  - step-05-patterns
  - step-06-structure
  - step-07-validation
  - step-08-complete
lastStep: 8
status: 'complete'
completedAt: '2026-03-08'
inputDocuments:
  - 'prd.md'
workflowType: 'architecture'
project_name: 'FinTech_Hackathon'
user_name: 'Aanya'
date: '2026-03-08'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
31 FRs across 7 capability areas. The architecture must support a linear data pipeline (ingest → cluster → score → enrich → display) with two AI integration points (theme clustering and causal chain generation). Key capability areas:
- News Data Ingestion (FR1-5): Batch pipeline pulling from free-tier APIs with caching and fallback
- Theme Intelligence (FR6-10): Clustering, scoring, tagging, and trend tracking
- Causal Chain Reasoning (FR11-14): Claude API integration with caching and disclaimers
- Institutional Memory (FR15-18): Historical storage, search, and pattern surfacing
- Dashboard & Navigation (FR19-25): SPA with theme feed, detail views, timelines, and search
- Article Intelligence (FR26-28): AI summaries and source attribution
- System Operations (FR29-31): Scheduled ingestion, rate limiting, cached serving

**Non-Functional Requirements:**
15 NFRs driving architectural decisions:
- Performance: 3s dashboard load, 1s detail view, 2s causal chain, 500ms search, 60s ingestion cycle
- Security: Environment variable API key storage, no auth required for prototype
- Integration: Graceful degradation on all external API failures, timeout handling, fallback behavior
- Data Quality: 5-15 themes per cycle, 30-word article summaries, consistent causal chain format

**Scale & Complexity:**
- Primary domain: Full-stack web (React + Python + PostgreSQL + Redis)
- Complexity level: Medium (well-scoped prototype with real data pipelines and LLM integration)
- Estimated architectural components: 8-10 (API server, ingestion worker, clustering service, Claude integration, Redis cache, PostgreSQL store, React SPA, scheduled task runner)

### Technical Constraints & Dependencies

- **Zero budget:** All external services must be free-tier (NewsAPI, GDELT, Google News RSS)
- **Claude API:** Available but cost-conscious — selective generation for hot themes only, aggressive caching
- **No authentication:** Open-access dashboard, no user management, no session handling
- **3-person team:** Frontend/backend split — architecture must support parallel development with clear API contract
- **3-day timeline:** Architecture must be simple enough to implement quickly — no over-engineering
- **Local development only:** No cloud deployment infrastructure needed for the prototype

### Cross-Cutting Concerns Identified

- **Caching strategy:** Redis sits between every external dependency and the frontend. All API responses cached. All AI-generated content cached. Dashboard always serves from cache.
- **Error handling / graceful degradation:** Every external API call (news, Claude) must have fallback behavior. No single API failure crashes the application.
- **AI content labeling:** All AI-generated content (summaries, causal chains) must be clearly labeled as AI-generated with financial disclaimer.
- **Rate limit management:** Batch scheduling must prevent exceeding free-tier quotas across all news APIs. Daily token budget for Claude API.
- **Data freshness tracking:** "Last updated" timestamps throughout so users know data currency when serving from cache.

## Starter Template Evaluation

### Primary Technology Domain

Full-stack web application with separate frontend and backend directories. React SPA frontend consuming a Python REST API backend, with PostgreSQL for persistence and Redis for caching.

### Starter Options Considered

**Frontend:**

| Option | Pros | Cons |
|---|---|---|
| Vite + React (selected) | Fast HMR, minimal config, modern defaults, lightweight | Less opinionated — need to add routing, state management manually |
| Create React App | Familiar, well-documented | Deprecated/unmaintained, slow builds, heavy |
| Next.js | SSR, file-based routing, API routes | Overkill for SPA dashboard, adds complexity |

**Backend:**

| Option | Pros | Cons |
|---|---|---|
| Flask (selected) | Simple, minimal, fast to prototype, team familiarity | No built-in async, manual API docs |
| FastAPI | Auto-docs, async, type validation | Steeper learning curve, async complexity for simple prototype |
| Django | Admin panel, ORM, batteries included | Heavy for an API-only backend, slow to iterate |

### Selected Starters

**Frontend: Vite + React**

**Initialization Command:**

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install react-router-dom zustand axios recharts tailwindcss @tailwindcss/vite
```

**Backend: Flask**

**Initialization Command:**

```bash
mkdir backend && cd backend
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors psycopg2-binary redis anthropic requests apscheduler
pip freeze > requirements.txt
```

### Architectural Decisions Provided by Starters

**Language & Runtime:**
- Frontend: JavaScript (React 19 via Vite template)
- Backend: Python 3.11+ (Flask)

**Styling Solution:**
- Tailwind CSS via Vite plugin — utility-first, rapid UI development, no CSS file management

**Build Tooling:**
- Frontend: Vite (esbuild for dev, Rollup for production builds)
- Backend: No build step — Python runs directly

**Code Organization:**
- Frontend: `src/components/`, `src/pages/`, `src/api/`, `src/store/`
- Backend: `app/`, `app/routes/`, `app/services/`, `app/models/`

**Development Experience:**
- Frontend: Vite HMR (instant hot reload), React DevTools
- Backend: Flask debug mode with auto-reload
- Both run locally — no Docker required for dev

**Key Libraries:**
- `react-router-dom` — client-side routing
- `zustand` — lightweight state management
- `axios` — HTTP client for API calls
- `recharts` — theme timeline charts
- `flask-cors` — CORS handling for React ↔ Flask communication
- `psycopg2-binary` — PostgreSQL adapter
- `redis` — Redis client
- `anthropic` — Claude API SDK
- `requests` — HTTP client for news API calls
- `apscheduler` — Scheduled news ingestion (every 30 min)

**Note:** Project initialization using these commands should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Database schema and query approach (raw SQL via psycopg2)
- API endpoint structure (resource-based REST)
- Frontend-backend API contract (defined upfront for parallel development)
- Environment configuration (.env with python-dotenv)
- Scheduled task approach (APScheduler in Flask process)

**Important Decisions (Shape Architecture):**
- Caching key strategy for Redis
- Claude API prompt structure and caching TTL
- Theme clustering algorithm approach

**Deferred Decisions (Post-MVP):**
- Database migrations tooling
- Production deployment infrastructure
- Monitoring and logging

### Data Architecture

**Database:** PostgreSQL with raw SQL via psycopg2-binary
- No ORM — direct SQL queries for simplicity and full control
- Connection pooling via psycopg2 connection pool
- Schema managed via a single `schema.sql` file executed on first run

**Cache:** Redis for all hot data
- Theme feed (full list with scores) — TTL: 5 minutes
- Individual causal chains — TTL: 2 hours (themes don't shift that fast)
- Article summaries — TTL: 24 hours (summaries don't change)
- News API responses — TTL: 30 minutes (matches ingestion cycle)
- Key naming convention: `macro:{resource}:{id}` (e.g. `macro:theme:fed-policy`, `macro:causal:fed-policy`, `macro:articles:fed-policy`)

**Schema Design (core tables):**

```sql
-- Articles ingested from news APIs
articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_name VARCHAR(255),
    url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMP,
    full_text TEXT,
    ai_summary TEXT,
    region_tags TEXT[],
    asset_tags TEXT[],
    theme_id INTEGER REFERENCES themes(id),
    ingested_at TIMESTAMP DEFAULT NOW()
)

-- Macro themes detected by clustering
themes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    score_label VARCHAR(10),  -- 'hot', 'warming', 'cool'
    score_value FLOAT,
    article_count INTEGER DEFAULT 0,
    region_tags TEXT[],
    asset_tags TEXT[],
    causal_chain JSONB,  -- structured: {trigger, mechanism, asset_impacts: [{asset_class, direction, explanation}]}
    causal_chain_generated_at TIMESTAMP,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_updated_at TIMESTAMP DEFAULT NOW()
)

-- Historical snapshots for institutional memory
theme_history (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER REFERENCES themes(id),
    snapshot_date DATE,
    score_label VARCHAR(10),
    score_value FLOAT,
    article_count INTEGER,
    causal_chain TEXT
)

-- Ingestion run tracking
ingestion_logs (
    id SERIAL PRIMARY KEY,
    run_at TIMESTAMP DEFAULT NOW(),
    articles_fetched INTEGER,
    articles_new INTEGER,
    themes_updated INTEGER,
    status VARCHAR(50),
    error_message TEXT
)
```

### Authentication & Security

- **No authentication** — open-access dashboard for hackathon prototype
- **API key protection** — all keys (NEWS_API_KEY, ANTHROPIC_API_KEY, DATABASE_URL, REDIS_URL) stored in `.env` file, loaded via `python-dotenv`, never committed to repo
- **`.gitignore`** — must include `.env`, `.env.production`, `venv/`, `__pycache__/`, `node_modules/`
- **CORS** — `flask-cors` configured to allow requests from `http://localhost:5173` (Vite dev server)

### API & Communication Patterns

**Design:** Resource-based REST API with JSON responses

**Base URL:** `http://localhost:5000/api`

**API Contract:**

| Method | Endpoint | Description | Response |
|---|---|---|---|
| GET | `/api/themes` | List all themes ranked by score | `[{id, name, slug, score_label, score_value, article_count, region_tags, asset_tags}]` |
| GET | `/api/themes/:slug` | Theme detail with articles and causal chain | `{theme, articles[], causal_chain{trigger, mechanism, asset_impacts[]}, article_dates[]}` |
| GET | `/api/themes/:slug/articles?date=:date` | Articles for a theme filtered by date (last 30 days only) | `[{id, title, source_name, url, published_at, ai_summary}]` |
| GET | `/api/articles?theme=:slug` | Articles for a specific theme | `[{id, title, source_name, url, published_at, ai_summary}]` |
| GET | `/api/memory/search?q=:query` | Search historical themes | `[{theme_name, snapshot_date, score_label, article_count, causal_chain}]` |
| GET | `/api/status` | System health / last ingestion info | `{last_ingestion, articles_count, themes_count, status}` |

**Error Handling Standard:**
```json
{
    "error": true,
    "message": "Human-readable error description",
    "code": "RATE_LIMIT_EXCEEDED"
}
```

**Response Envelope:**
All successful responses wrapped in: `{"data": ..., "meta": {"last_updated": "ISO timestamp"}}`

### Frontend Architecture

- **State Management:** Zustand store for theme data, selected theme, and search state
- **Routing:** React Router with 2 routes: `/` (theme feed) and `/theme/:slug` (theme detail)
- **Component Architecture:** Flat component structure in `src/components/` — no nested folders for hackathon simplicity
- **API Client:** Axios instance in `src/api/client.js` with base URL configuration and error interceptor
- **Data Fetching:** Axios calls in components via useEffect — no React Query or SWR needed for this scope

### Infrastructure & Deployment

**Docker Compose** — single `docker-compose.yml` at project root runs the entire stack identically on Mac, Windows, and Linux. Same configuration for local development and production deployment.

**Services (4 containers):**

| Service | Image | Port | Notes |
|---|---|---|---|
| `frontend` | Custom (Vite build + nginx) | 80/443 | Multi-stage build: npm build → nginx serves static files + proxies /api to backend |
| `backend` | Custom (Flask + gunicorn) | 5000 (internal) | Gunicorn in production, Flask dev server in dev. APScheduler runs in-process. |
| `postgres` | `postgres:16-alpine` | 5432 (internal) | Volume-mounted for data persistence. Schema auto-applied via init script. |
| `redis` | `redis:7-alpine` | 6379 (internal) | Ephemeral cache — no persistence needed. |

**Local Development:**
- `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up` — mounts source code, enables hot reload for both frontend (Vite HMR) and backend (Flask debug mode)
- Frontend accessible at `http://localhost:3000`, backend at `http://localhost:5000`
- Or run frontend/backend natively outside Docker for faster iteration, connecting to Dockerized PostgreSQL + Redis

**Production Deployment (AWS EC2 + Cloudflare):**
- **EC2 instance:** t3.small (2 vCPU, 2GB RAM) — sufficient for hackathon demo traffic
- **Setup:** SSH into EC2, clone repo, copy `.env.production`, run `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
- **Cloudflare:** DNS pointing to EC2 elastic IP, free SSL via Cloudflare proxy, CDN caching for static assets
- **nginx** in frontend container handles: serving React build, proxying `/api/*` to Flask backend, SSL termination handled by Cloudflare

**Docker Files:**

```
project-root/
├── docker-compose.yml              # Base services definition
├── docker-compose.dev.yml          # Dev overrides (volume mounts, hot reload)
├── docker-compose.prod.yml         # Prod overrides (gunicorn, restart policies)
├── frontend/
│   ├── Dockerfile                  # Multi-stage: node build → nginx serve
│   └── nginx.conf                  # Static serving + /api proxy
├── backend/
│   ├── Dockerfile                  # Python + gunicorn
│   └── .env.example                # Template for environment variables
└── .env.production                 # Production secrets (never committed)
```

**Environment Management:**
- `.env` — local development secrets (git-ignored)
- `.env.production` — production secrets on EC2 only (git-ignored)
- `.env.example` — template with all required variables (committed)
- Variables: `DATABASE_URL`, `REDIS_URL`, `ANTHROPIC_API_KEY`, `NEWS_API_KEY`, `FLASK_ENV`, `VITE_API_URL`

**nginx Configuration (frontend/nginx.conf):**
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Decision Impact Analysis

**Implementation Sequence:**
1. Docker Compose setup with all 4 services + PostgreSQL schema creation (`schema.sql`)
2. Flask app scaffold with API endpoints returning mock data
3. React app scaffold with Vite, routing, and Axios client hitting Flask API
4. News ingestion service + APScheduler integration
5. Theme clustering service
6. Claude API integration for causal chains
7. Connect real data through all layers
8. Institutional memory (history snapshots + search endpoint)
9. Production Dockerfiles (multi-stage frontend, gunicorn backend) + nginx config
10. AWS EC2 deployment + Cloudflare DNS setup

**Cross-Component Dependencies:**
- Frontend depends on API contract (defined above) — can use mock data until backend is ready
- Causal chain generation depends on theme clustering — themes must exist before Claude can reason about them
- Institutional memory depends on theme_history table being populated over time (pre-seed for demo)
- APScheduler depends on all ingestion + clustering services being functional

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 12 areas where AI agents could make different choices, now resolved with explicit patterns.

### Naming Patterns

**Database Naming Conventions:**
- Tables: `snake_case`, plural (`articles`, `themes`, `theme_history`, `ingestion_logs`)
- Columns: `snake_case` (`score_value`, `article_count`, `published_at`)
- Foreign keys: `{referenced_table_singular}_id` (`theme_id`)
- Indexes: `idx_{table}_{column}` (`idx_articles_theme_id`)
- Constraints: `{table}_{column}_{type}` (`articles_url_unique`)

**API Naming Conventions:**
- Endpoints: plural nouns, lowercase (`/api/themes`, `/api/articles`)
- Route parameters: `:param_name` (`/api/themes/:slug`)
- Query parameters: `snake_case` (`?theme=fed-policy`)
- JSON fields: `snake_case` in both request and response bodies (`score_label`, `article_count`, `last_updated`)

**Frontend Code Naming:**
- React components: `PascalCase` files and exports (`ThemeCard.jsx`, `CausalChain.jsx`)
- Component folders: None — flat structure in `src/components/`
- Hooks: `camelCase` with `use` prefix (`useThemeStore.js`)
- Utility files: `camelCase` (`formatDate.js`, `apiClient.js`)
- CSS/style: Tailwind utility classes inline — no separate CSS files
- Constants: `UPPER_SNAKE_CASE` (`API_BASE_URL`, `CACHE_TTL`)

**Backend Code Naming:**
- Python files: `snake_case` (`theme_service.py`, `news_ingestion.py`)
- Functions: `snake_case` (`get_themes`, `fetch_articles`)
- Classes: `PascalCase` (`ThemeClusterer`, `CausalChainGenerator`)
- Variables: `snake_case` (`article_count`, `theme_slug`)
- Route files: `snake_case` matching resource (`themes.py`, `articles.py`)

### Structure Patterns

**Frontend Organization:**
```
frontend/src/
├── components/       # All React components (flat, no nesting)
│   ├── ThemeCard.jsx
│   ├── ThemeFeed.jsx
│   ├── ThemeDetail.jsx
│   ├── CausalChain.jsx
│   ├── ArticleList.jsx
│   ├── DateTimeline.jsx
│   ├── SearchBar.jsx
│   └── StatusBadge.jsx
├── pages/            # Route-level page components
│   ├── DashboardPage.jsx
│   └── ThemeDetailPage.jsx
├── api/              # API client and endpoint functions
│   └── client.js
├── store/            # Zustand stores
│   └── useThemeStore.js
├── App.jsx
└── main.jsx
```

**Backend Organization:**
```
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/
│   │   ├── themes.py
│   │   ├── articles.py
│   │   ├── memory.py
│   │   └── status.py
│   ├── services/
│   │   ├── news_ingestion.py
│   │   ├── theme_clustering.py
│   │   ├── causal_chain.py
│   │   └── article_summarizer.py
│   ├── models/
│   │   └── db.py            # Database connection + raw SQL queries
│   └── utils/
│       ├── cache.py         # Redis helper functions
│       └── config.py        # Environment variable loading
├── Dockerfile                 # Python + gunicorn
├── schema.sql
├── run.py
├── requirements.txt
├── .env
└── .env.example
```

**Project Root (Docker & Deployment):**
```
project-root/
├── docker-compose.yml          # Base services (frontend, backend, postgres, redis)
├── docker-compose.dev.yml      # Dev overrides (volume mounts, hot reload)
├── docker-compose.prod.yml     # Prod overrides (gunicorn, restart policies)
├── .env.production             # Production secrets (git-ignored)
├── .gitignore
├── README.md
├── frontend/
│   ├── Dockerfile              # Multi-stage: node build → nginx serve
│   ├── nginx.conf              # Static serving + /api proxy
│   └── ...
└── backend/
    ├── Dockerfile              # Python + gunicorn
    └── ...
```

### Format Patterns

**API Response Format:**
```json
// Success
{
    "data": { ... },
    "meta": { "last_updated": "2026-03-08T14:30:00Z" }
}

// Success (list)
{
    "data": [ ... ],
    "meta": { "last_updated": "2026-03-08T14:30:00Z", "count": 12 }
}

// Error
{
    "error": true,
    "message": "Human-readable error description",
    "code": "RATE_LIMIT_EXCEEDED"
}
```

**Date/Time Format:**
- All timestamps in ISO 8601 format: `2026-03-08T14:30:00Z`
- Display formatting handled by frontend only
- Database stores `TIMESTAMP` types, API serializes to ISO strings

**Null Handling:**
- Null fields included in response with `null` value (not omitted)
- Frontend checks for null before rendering, shows placeholder text (e.g., "Causal chain generating..." or "No summary available")

### Communication Patterns

**State Management (Zustand):**
```javascript
// Store pattern — single store with slices
const useThemeStore = create((set) => ({
    themes: [],
    selected_theme: null,
    loading: false,
    error: null,

    set_themes: (themes) => set({ themes }),
    set_selected_theme: (theme) => set({ selected_theme: theme }),
    set_loading: (loading) => set({ loading }),
    set_error: (error) => set({ error }),
}))
```

- Action names: `snake_case` matching the state field (`set_themes`, `set_error`)
- State fields: `snake_case` to match API response format
- Single store file — no need for multiple stores at this scale

**API Client Pattern:**
```javascript
// src/api/client.js
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    timeout: 10000,
})

// All API functions exported from same file
export const fetchThemes = () => api.get('/themes')
export const fetchThemeDetail = (slug) => api.get(`/themes/${slug}`)
export const searchMemory = (query) => api.get('/memory/search', { params: { q: query } })
```

### Process Patterns

**Loading & Error States (Per-Component):**
- Each component that fetches data manages its own `loading` and `error` state
- Pattern:
```jsx
function ThemeFeed() {
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // ... fetch with try/catch, set loading/error accordingly

    if (loading) return <div className="animate-pulse">Loading themes...</div>
    if (error) return <div className="text-red-500">Failed to load themes</div>
    return <div>...</div>
}
```
- No global loading spinner — each section loads independently
- Stale data shown while refreshing (cache-first approach)

**Backend Error Handling:**
- All route handlers wrapped in try/except
- External API failures return cached data with stale `last_updated` timestamp
- If no cache exists, return error response with appropriate HTTP status
- Pattern:
```python
@app.route('/api/themes')
def get_themes():
    try:
        cached = redis_client.get('macro:themes:all')
        if cached:
            return jsonify({"data": json.loads(cached), "meta": {"last_updated": get_cache_time('macro:themes:all')}})
        themes = fetch_themes_from_db()
        redis_client.setex('macro:themes:all', 300, json.dumps(themes))
        return jsonify({"data": themes, "meta": {"last_updated": datetime.utcnow().isoformat() + 'Z'}})
    except Exception as e:
        return jsonify({"error": True, "message": str(e), "code": "INTERNAL_ERROR"}), 500
```

**AI Content Labeling:**
- All AI-generated content (summaries, causal chains) must include visual indicator
- Frontend: Use a consistent "AI-Generated" badge component
- Causal chains must include disclaimer: *"AI-generated analysis for informational purposes only. Not financial advice."*

### Enforcement Guidelines

**All AI Agents MUST:**
- Use `snake_case` for all JSON fields, Python code, database columns, and API parameters
- Use `PascalCase` for React component files and exports only
- Wrap all API responses in `{"data": ..., "meta": {"last_updated": ...}}` envelope
- Include try/except on every external API call with fallback to cached data
- Label all AI-generated content with disclaimer text
- Use the `macro:{resource}:{id}` Redis key convention
- Never hardcode API keys — always read from environment variables

### Anti-Patterns to Avoid

- `camelCase` JSON fields (`articleCount`) — use `snake_case` (`article_count`)
- `themeCard.jsx` or `theme-card.jsx` — use `ThemeCard.jsx`
- Bare API response `[{...}]` — use wrapped `{"data": [{...}], "meta": {...}}`
- Silent API failures — always return error response or cached fallback
- Global loading spinner — use per-component loading states
- `redis.get('themes')` — use `redis.get('macro:themes:all')`

## Project Structure & Boundaries

### Complete Project Directory Structure

```
FinTech_Hackathon/
├── README.md
├── .gitignore
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css                  # Tailwind imports
│       ├── components/
│       │   ├── ThemeCard.jsx           # Single theme card in feed
│       │   ├── ThemeFeed.jsx           # List of theme cards
│       │   ├── ThemeDetail.jsx         # Full theme view with causal chain
│       │   ├── CausalChain.jsx         # Causal chain display with disclaimer
│       │   ├── ArticleList.jsx         # Articles for a theme
│       │   ├── DateTimeline.jsx       # Interactive date navigation with article filtering
│       │   ├── SearchBar.jsx           # Institutional memory search
│       │   ├── StatusBadge.jsx         # Hot/warming/cool score badge
│       │   └── Disclaimer.jsx          # AI-generated content disclaimer
│       ├── pages/
│       │   ├── DashboardPage.jsx       # Route: /
│       │   └── ThemeDetailPage.jsx     # Route: /theme/:slug
│       ├── api/
│       │   └── client.js              # Axios instance + all API functions
│       └── store/
│           └── useThemeStore.js        # Zustand store
│
├── backend/
│   ├── run.py                          # Flask app entry point
│   ├── requirements.txt
│   ├── schema.sql                      # PostgreSQL schema (4 tables)
│   ├── .env                            # API keys, DB/Redis URLs (gitignored)
│   ├── .env.example                    # Template with placeholder values
│   └── app/
│       ├── __init__.py                 # Flask app factory + CORS setup
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── themes.py              # /api/themes, /api/themes/:slug, /api/themes/:slug/articles?date=
│       │   ├── articles.py            # /api/articles?theme=:slug
│       │   ├── memory.py              # /api/memory/search?q=:query
│       │   └── status.py             # /api/status
│       ├── services/
│       │   ├── __init__.py
│       │   ├── news_ingestion.py      # NewsAPI, GDELT, Google News RSS fetching
│       │   ├── theme_clustering.py    # Article → theme clustering + scoring
│       │   ├── causal_chain.py        # Claude API integration for causal chains
│       │   ├── article_summarizer.py  # Claude API for 30-word summaries
│       │   └── scheduler.py           # APScheduler setup (30-min ingestion cycle)
│       ├── models/
│       │   ├── __init__.py
│       │   └── db.py                  # PostgreSQL connection pool + query functions
│       └── utils/
│           ├── __init__.py
│           ├── cache.py               # Redis get/set/delete helpers with TTL
│           └── config.py              # python-dotenv environment loading
│
└── _bmad-output/                       # Planning artifacts (gitignored from prod)
    └── planning-artifacts/
        ├── prd.md
        └── architecture.md
```

### Architectural Boundaries

**API Boundaries:**
- Frontend ↔ Backend: REST API over HTTP (`localhost:5000/api`)
- Backend ↔ News APIs: HTTP via `requests` library (NewsAPI, GDELT, Google News RSS)
- Backend ↔ Claude API: `anthropic` SDK for causal chains and summaries
- Backend ↔ PostgreSQL: `psycopg2` connection pool, raw SQL
- Backend ↔ Redis: `redis-py` client for all caching

**Component Boundaries:**
- `routes/` — HTTP request/response only; delegates all logic to `services/`
- `services/` — business logic; calls `models/db.py` for data and `utils/cache.py` for caching
- `models/db.py` — sole database access point; all SQL queries defined here
- `utils/cache.py` — sole Redis access point; all cache key generation here
- Frontend components fetch via `api/client.js` only — no direct HTTP calls in components

**Data Boundaries:**
- PostgreSQL: persistent storage (articles, themes, history, logs)
- Redis: ephemeral cache layer — all reads check cache first, all writes update cache
- No direct frontend-to-database connection — all data flows through Flask API

### Requirements to Structure Mapping

| FR Category | Backend Location | Frontend Location |
|---|---|---|
| News Data Ingestion (FR1-5) | `services/news_ingestion.py`, `services/scheduler.py` | — |
| Theme Intelligence (FR6-10) | `services/theme_clustering.py`, `routes/themes.py` | `ThemeFeed.jsx`, `ThemeCard.jsx`, `StatusBadge.jsx` |
| Causal Chain Reasoning (FR11-14) | `services/causal_chain.py`, `routes/themes.py` | `CausalChain.jsx`, `Disclaimer.jsx` |
| Institutional Memory (FR15-18) | `routes/memory.py`, `models/db.py` | `SearchBar.jsx` |
| Dashboard & Navigation (FR19-25) | `routes/themes.py`, `routes/articles.py` | `DashboardPage.jsx`, `ThemeDetailPage.jsx`, `DateTimeline.jsx` |
| Article Intelligence (FR26-28) | `services/article_summarizer.py` | `ArticleList.jsx` |
| System Operations (FR29-31) | `services/scheduler.py`, `routes/status.py`, `utils/cache.py` | — |

### Integration Points

**Data Flow:**
```
News APIs → news_ingestion.py → articles table
                                      ↓
                              theme_clustering.py → themes table
                                      ↓
                              causal_chain.py → themes.causal_chain
                              (Claude API)      → Redis cache
                                      ↓
                              Flask routes → JSON response → React SPA
```

**External Integrations:**

| Service | Module | Rate Limits | Fallback |
|---|---|---|---|
| NewsAPI | `news_ingestion.py` | 100 req/day (free) | Return cached articles |
| GDELT | `news_ingestion.py` | Unlimited | Skip if unavailable |
| Google News RSS | `news_ingestion.py` | Best-effort | Skip if unavailable |
| Claude API | `causal_chain.py`, `article_summarizer.py` | Token budget/day | Return cached or "Generating..." |

### Development Workflow

**Startup (two terminals):**
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && python run.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

**Parallel Development:**
- Aanya (frontend): Works against mock data or live API — `api/client.js` base URL points to `localhost:5000`
- Akul + Saanvi (backend): Build services and routes — test via curl or Postman
- API contract (defined in architecture doc) is the shared interface

## Architecture Validation Results

### Coherence Validation

**Decision Compatibility:** All technology choices are compatible:
- Vite + React 19 + Tailwind CSS — well-tested combination
- Flask + psycopg2 + redis-py + anthropic SDK — all standard Python libraries, no conflicts
- APScheduler runs in-process with Flask — simple and appropriate for prototype
- CORS configured for Vite dev server port (5173) → Flask (5000)

**Pattern Consistency:** All patterns align:
- `snake_case` used consistently across JSON, Python, database, and API parameters
- `PascalCase` used only for React components and Python classes — no ambiguity
- Redis key convention (`macro:{resource}:{id}`) applied uniformly
- Response envelope (`{data, meta}`) specified for all endpoints

**Structure Alignment:** Project structure supports all decisions:
- `routes/` → `services/` → `models/` layering enforces separation of concerns
- Single `db.py` and `cache.py` prevent multiple access patterns
- Flat component structure matches hackathon simplicity goal

### Requirements Coverage Validation

**Functional Requirements (31 FRs across 7 categories):**

| Category | FRs | Covered By | Status |
|---|---|---|---|
| News Data Ingestion | FR1-5 | `news_ingestion.py`, `scheduler.py`, `db.py` | Covered |
| Theme Intelligence | FR6-10 | `theme_clustering.py`, `themes.py` route | Covered |
| Causal Chain Reasoning | FR11-14 | `causal_chain.py`, Claude API, `cache.py` | Covered |
| Institutional Memory | FR15-18 | `theme_history` table, `memory.py` route, `SearchBar.jsx` | Covered |
| Dashboard & Navigation | FR19-25 | React SPA, 2 routes, all components | Covered |
| Article Intelligence | FR26-28 | `article_summarizer.py`, `ArticleList.jsx` | Covered |
| System Operations | FR29-31 | `scheduler.py`, `status.py`, `cache.py` | Covered |

**Non-Functional Requirements (15 NFRs):**

| NFR | Architectural Support |
|---|---|
| 3s dashboard load | Redis cache (5-min TTL) serves pre-computed theme feed |
| 1s detail view | Redis-cached theme detail + articles |
| 2s causal chain | Pre-generated and cached (2-hr TTL), not on-demand |
| 500ms search | PostgreSQL full-text search on theme_history |
| 60s ingestion cycle | APScheduler batch processing |
| API key security | `.env` + `python-dotenv`, `.gitignore` |
| Graceful degradation | try/except on all external calls, cache fallback |
| 5-15 themes per cycle | Clustering service output constraint |
| 30-word summaries | Claude API prompt constraint |

### Implementation Readiness Validation

**Decision Completeness:** All critical decisions documented with specific libraries, versions implied by starter commands, and concrete code examples for patterns.

**Structure Completeness:** Every file and directory specified with purpose annotations. No generic placeholders.

**Pattern Completeness:** Naming, structure, format, communication, and process patterns all have concrete examples and anti-patterns.

### Gap Analysis Results

**No critical gaps found.**

**Minor gaps (non-blocking for hackathon):**
- No database migration tooling specified — acceptable since `schema.sql` is run once
- No logging strategy specified — `print()` statements sufficient for prototype
- No specific clustering algorithm chosen — will be decided during implementation (TF-IDF + cosine similarity likely)
- No seed data strategy for demo — may want to pre-populate `theme_history` for institutional memory demo

### Architecture Completeness Checklist

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified (zero budget, 3-day timeline, 3-person team)
- [x] Cross-cutting concerns mapped (caching, error handling, AI labeling, rate limits)
- [x] Critical decisions documented with specific libraries
- [x] Technology stack fully specified (React/Vite + Flask + PostgreSQL + Redis)
- [x] Integration patterns defined (REST API, cache-first reads, batch ingestion)
- [x] Performance considerations addressed (Redis TTLs, pre-generated content)
- [x] Naming conventions established (snake_case everywhere except PascalCase components)
- [x] Structure patterns defined (flat components, layered backend)
- [x] Communication patterns specified (Zustand store, Axios client)
- [x] Process patterns documented (per-component loading, try/except + cache fallback)
- [x] Complete directory structure defined
- [x] Component boundaries established (routes → services → models)
- [x] Integration points mapped (4 external services with fallbacks)
- [x] Requirements to structure mapping complete (all 31 FRs mapped)

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- Clear separation enabling parallel frontend/backend development
- API contract defined upfront — Aanya can build UI while Akul + Saanvi build services
- Cache-first architecture ensures dashboard always loads, even during API failures
- Simple, hackathon-appropriate decisions — no over-engineering

**Areas for Future Enhancement (post-hackathon):**
- Database migration tooling (Alembic)
- Structured logging
- Monitoring and alerting
- Authentication and user management
- Cloud deployment infrastructure

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and boundaries
- Refer to this document for all architectural questions

**First Implementation Priority:**
1. Run starter commands (Vite + Flask scaffold)
2. Execute `schema.sql` against local PostgreSQL
3. Configure `.env` with API keys and connection strings
4. Verify Flask → PostgreSQL → Redis connectivity
5. Build mock API endpoints returning hardcoded data
6. Build React shell with routing and Axios client
