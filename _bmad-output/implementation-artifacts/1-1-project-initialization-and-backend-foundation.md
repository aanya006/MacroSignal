# Story 1.1: Project Initialization & Backend Foundation

Status: ready-for-dev

## Story

As a developer,
I want a fully initialized project with Vite+React frontend, Flask backend, PostgreSQL database, and Redis cache,
so that all subsequent stories have a working foundation to build on.

## Acceptance Criteria

1. **Given** the project repository is cloned **When** the developer runs the setup commands **Then** a Vite + React frontend starts on localhost:5173 with Tailwind CSS configured
2. **Given** the frontend is initialized **When** the dev server starts **Then** React Router is configured with 2 routes (/ and /theme/:slug) and Zustand store is initialized
3. **Given** the backend directory exists **When** the Flask app starts **Then** it runs on localhost:5000 with flask-cors configured for localhost:5173
4. **Given** PostgreSQL is running **When** schema.sql is executed **Then** 4 tables are created: articles, themes, theme_history, ingestion_logs
5. **Given** Redis is running **When** the backend connects **Then** Redis is accessible for caching operations
6. **Given** environment is configured **When** .env file exists **Then** it contains placeholders for NEWS_API_KEY, ANTHROPIC_API_KEY, DATABASE_URL, REDIS_URL
7. **Given** the project is set up **When** GET /api/status is called **Then** it returns {"data": {"status": "ok"}, "meta": {"last_updated": "ISO timestamp"}}
8. **Given** .gitignore is configured **When** checking tracked files **Then** .env, venv/, node_modules/, __pycache__/ are excluded

## Tasks / Subtasks

- [ ] Task 1: Initialize Frontend (AC: #1, #2)
  - [ ] Run `npm create vite@latest frontend -- --template react`
  - [ ] Install dependencies: `react-router-dom zustand axios tailwindcss @tailwindcss/vite`
  - [ ] Configure Tailwind in vite.config.js via @tailwindcss/vite plugin
  - [ ] Add Tailwind import to src/index.css: `@import "tailwindcss";`
  - [ ] Set up React Router in App.jsx with / and /theme/:slug routes
  - [ ] Create placeholder page components: DashboardPage.jsx, ThemeDetailPage.jsx
  - [ ] Create Zustand store: src/store/useThemeStore.js
  - [ ] Create API client: src/api/client.js with Axios instance (baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api')
- [ ] Task 2: Initialize Backend (AC: #3, #5, #6)
  - [ ] Create backend/ directory with venv
  - [ ] Install: flask flask-cors psycopg2-binary redis anthropic requests apscheduler python-dotenv
  - [ ] Create requirements.txt via pip freeze
  - [ ] Create app/__init__.py with Flask app factory + CORS setup
  - [ ] Create run.py entry point
  - [ ] Create utils/config.py for environment variable loading via python-dotenv
  - [ ] Create utils/cache.py with Redis connection helper
  - [ ] Create models/db.py with PostgreSQL connection pool
  - [ ] Create .env with placeholder values
  - [ ] Create .env.example with same placeholders (committed to repo)
- [ ] Task 3: Database Schema (AC: #4)
  - [ ] Create backend/schema.sql with all 4 tables: articles, themes, theme_history, ingestion_logs
  - [ ] Include indexes: idx_articles_theme_id, idx_articles_published_at, idx_themes_slug
  - [ ] Include constraints: articles_url_unique
  - [ ] NOTE: score_label uses values 'hot', 'warm', 'cool' (NOT 'warming' — updated in planning)
- [ ] Task 4: Status Endpoint (AC: #7)
  - [ ] Create routes/status.py with GET /api/status
  - [ ] Return response envelope: {"data": {...}, "meta": {"last_updated": "ISO timestamp"}}
  - [ ] Register blueprint in app factory
- [ ] Task 5: Verify End-to-End (AC: #8)
  - [ ] Update .gitignore (already exists at project root — verify it covers venv/, __pycache__/)
  - [ ] Verify frontend starts and renders placeholder page
  - [ ] Verify backend starts and /api/status returns valid JSON
  - [ ] Verify PostgreSQL connection and schema creation
  - [ ] Verify Redis connection

## Dev Notes

### Architecture Compliance

- **Database:** PostgreSQL with raw SQL via psycopg2-binary. NO ORM. Connection pooling via psycopg2.
- **Cache:** Redis client via redis-py. Key convention: `macro:{resource}:{id}`
- **Response envelope:** ALL API responses must use `{"data": ..., "meta": {"last_updated": "ISO timestamp"}}`
- **Error format:** `{"error": true, "message": "...", "code": "ERROR_CODE"}`
- **Naming:** snake_case everywhere (Python, JSON, DB columns, API params). PascalCase for React components and Python classes only.
- **No auth required** — open access prototype

### Initialization Commands (from Architecture Doc)

**Frontend:**
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install react-router-dom zustand axios tailwindcss @tailwindcss/vite
```

**Backend:**
```bash
mkdir backend && cd backend
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors psycopg2-binary redis anthropic requests apscheduler python-dotenv
pip freeze > requirements.txt
```

### Database Schema (from Architecture Doc)

```sql
-- Articles ingested from news APIs
CREATE TABLE articles (
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
);

-- Macro themes detected by clustering
CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    score_label VARCHAR(10),  -- 'hot', 'warm', 'cool'
    score_value FLOAT,
    article_count INTEGER DEFAULT 0,
    region_tags TEXT[],
    asset_tags TEXT[],
    causal_chain JSONB,
    causal_chain_generated_at TIMESTAMP,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_updated_at TIMESTAMP DEFAULT NOW()
);

-- Historical snapshots for institutional memory
CREATE TABLE theme_history (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER REFERENCES themes(id),
    snapshot_date DATE,
    score_label VARCHAR(10),
    score_value FLOAT,
    article_count INTEGER,
    causal_chain TEXT
);

-- Ingestion run tracking
CREATE TABLE ingestion_logs (
    id SERIAL PRIMARY KEY,
    run_at TIMESTAMP DEFAULT NOW(),
    articles_fetched INTEGER,
    articles_new INTEGER,
    themes_updated INTEGER,
    status VARCHAR(50),
    error_message TEXT
);

CREATE INDEX idx_articles_theme_id ON articles(theme_id);
CREATE INDEX idx_articles_published_at ON articles(published_at);
CREATE INDEX idx_themes_slug ON themes(slug);
```

**IMPORTANT:** themes table must be created BEFORE articles table (foreign key dependency).

### Project Structure (from Architecture Doc)

```
frontend/src/
├── components/       # All React components (flat, no nesting)
├── pages/            # Route-level page components
│   ├── DashboardPage.jsx
│   └── ThemeDetailPage.jsx
├── api/
│   └── client.js     # Axios instance + API functions
├── store/
│   └── useThemeStore.js
├── App.jsx
├── index.css
└── main.jsx

backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/
│   │   ├── __init__.py
│   │   └── status.py        # /api/status (only endpoint for this story)
│   ├── services/             # Empty for now — populated in later stories
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── db.py            # PostgreSQL connection pool + query helpers
│   └── utils/
│       ├── __init__.py
│       ├── cache.py         # Redis helpers
│       └── config.py        # python-dotenv loading
├── schema.sql
├── run.py
├── requirements.txt
├── .env
└── .env.example
```

### Zustand Store Pattern (from Architecture Doc)

```javascript
import { create } from 'zustand'

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

export default useThemeStore
```

### API Client Pattern (from Architecture Doc)

```javascript
import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    timeout: 10000,
})

export const fetchThemes = () => api.get('/themes')
export const fetchThemeDetail = (slug) => api.get(`/themes/${slug}`)
export const fetchThemeArticles = (slug, date) => api.get(`/themes/${slug}/articles`, { params: { date } })
export const searchMemory = (query) => api.get('/memory/search', { params: { q: query } })
export const fetchStatus = () => api.get('/status')

export default api
```

### Flask App Factory Pattern (from Architecture Doc)

```python
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173"])

    from app.routes.status import status_bp
    app.register_blueprint(status_bp)

    return app
```

### Environment Variables (.env.example)

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/macrosignal
REDIS_URL=redis://localhost:6379/0
NEWS_API_KEY=your_newsapi_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
FLASK_ENV=development
VITE_API_URL=http://localhost:5000/api
```

### UX Notes

- Dark terminal aesthetic: background #0f172a, surfaces #1e293b
- Temperature colors: Hot=red, Warm=amber, Cool=cyan
- No emojis in any labels
- Tailwind CSS utility classes inline — no separate CSS files
- Placeholder pages should render with dark background to validate Tailwind setup

### Critical Warnings

- **DO NOT** use camelCase for JSON fields — use snake_case everywhere
- **DO NOT** create component subdirectories — flat structure in src/components/
- **DO NOT** hardcode API keys — always read from environment variables
- **DO NOT** use an ORM — raw SQL via psycopg2 only
- **DO NOT** use 'warming' as a score_label — the correct value is 'warm'
- **themes table MUST be created before articles table** in schema.sql (FK dependency)

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Starter-Options-Considered]
- [Source: _bmad-output/planning-artifacts/architecture.md#Data-Architecture]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project-Structure-&-Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation-Patterns-&-Consistency-Rules]
- [Source: _bmad-output/planning-artifacts/ux-design-specification.md#Design-Opportunities]
- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.1]

## Dev Agent Record

### Agent Model Used



### Debug Log References

### Completion Notes List

### File List


