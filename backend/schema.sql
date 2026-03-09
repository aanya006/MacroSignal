-- MacroSignal Database Schema
-- Run once to initialize: psql -d macrosignal -f schema.sql

-- Macro themes detected by clustering
CREATE TABLE IF NOT EXISTS themes (
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

-- Articles ingested from news APIs
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_name VARCHAR(255),
    url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMP,
    full_text TEXT,
    ai_summary TEXT,
    image_url TEXT,
    region_tags TEXT[],
    asset_tags TEXT[],
    theme_id INTEGER REFERENCES themes(id),
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Historical snapshots for institutional memory
CREATE TABLE IF NOT EXISTS theme_history (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER REFERENCES themes(id),
    snapshot_date DATE,
    score_label VARCHAR(10),
    score_value FLOAT,
    article_count INTEGER,
    causal_chain TEXT,
    UNIQUE(theme_id, snapshot_date)
);

-- Ingestion run tracking
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id SERIAL PRIMARY KEY,
    run_at TIMESTAMP DEFAULT NOW(),
    articles_fetched INTEGER,
    articles_new INTEGER,
    themes_updated INTEGER,
    status VARCHAR(50),
    error_message TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_articles_theme_id ON articles(theme_id);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_themes_slug ON themes(slug);
CREATE INDEX IF NOT EXISTS idx_theme_history_theme_id ON theme_history(theme_id);
CREATE INDEX IF NOT EXISTS idx_theme_history_snapshot_date ON theme_history(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_ingestion_logs_run_at ON ingestion_logs(run_at);
