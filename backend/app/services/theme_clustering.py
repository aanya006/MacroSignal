import json
import logging
import re
from datetime import datetime, timezone

from app.models.db import execute_query
from app.utils.cache import cache_set

logger = logging.getLogger(__name__)

# Predefined theme definitions with keyword matching
THEME_DEFINITIONS = {
    "fed-policy": {
        "name": "Fed Policy Trajectory",
        "keywords": ["federal reserve", "fed ", "fomc", "powell", "us interest rate", "fed funds", "fed rate"],
        "description": "US Federal Reserve monetary policy decisions and trajectory",
    },
    "mas-policy": {
        "name": "MAS Monetary Policy",
        "keywords": ["mas ", "monetary authority of singapore", "singapore dollar", "sgd", "neer", "s$neer", "mas policy"],
        "description": "Monetary Authority of Singapore policy and SGD management",
    },
    "china-economy": {
        "name": "China Economic Outlook",
        "keywords": ["china gdp", "china manufacturing", "pmi china", "chinese economy", "yuan", "pboc", "china growth", "china trade"],
        "description": "Chinese economic indicators, growth, and PBOC policy",
    },
    "us-inflation": {
        "name": "US Inflation & CPI",
        "keywords": ["us inflation", "cpi ", "consumer price", "pce ", "us prices", "inflation rate"],
        "description": "US inflation data, CPI releases, and price trends",
    },
    "global-trade": {
        "name": "Global Trade & Tariffs",
        "keywords": ["tariff", "trade war", "trade deal", "wto", "export ban", "import dut", "trade tension", "trade policy"],
        "description": "International trade disputes, tariffs, and trade agreements",
    },
    "oil-energy": {
        "name": "Oil & Energy Markets",
        "keywords": ["oil price", "crude oil", "opec", "brent", "energy market", "natural gas", "petroleum"],
        "description": "Oil prices, OPEC decisions, and global energy markets",
    },
    "ecb-europe": {
        "name": "ECB & European Economy",
        "keywords": ["ecb", "european central bank", "eurozone", "eu economy", "euro ", "lagarde"],
        "description": "European Central Bank policy and eurozone economy",
    },
    "boj-japan": {
        "name": "BOJ & Japan Economy",
        "keywords": ["boj", "bank of japan", "yen ", "japan economy", "yield curve control", "ueda", "japanese yen"],
        "description": "Bank of Japan policy, yen dynamics, and Japanese economy",
    },
    "emerging-markets": {
        "name": "Emerging Markets",
        "keywords": ["emerging market", "asean", "developing econom", "em bonds", "em currenc", "frontier market"],
        "description": "Emerging and frontier market economies and investments",
    },
    "tech-sector": {
        "name": "Technology Sector",
        "keywords": ["tech stock", "semiconductor", "ai stock", "nasdaq", "big tech", "chip", "nvidia", "tech sector"],
        "description": "Technology sector performance, semiconductors, and AI",
    },
    "geopolitical": {
        "name": "Geopolitical Risk",
        "keywords": ["geopolitical", "sanctions", "conflict", "military", "geopolitic", "tensions"],
        "description": "Geopolitical risks, sanctions, and global security events",
    },
    "bonds-rates": {
        "name": "Bond Markets & Yields",
        "keywords": ["bond yield", "treasury", "sovereign debt", "yield curve", "bond market", "government bond"],
        "description": "Global bond markets, treasury yields, and fixed income",
    },
    "fx-currency": {
        "name": "FX & Currency Markets",
        "keywords": ["forex", "currency", "exchange rate", "dollar index", "dxy", "fx market"],
        "description": "Foreign exchange markets and currency movements",
    },
    "commodities": {
        "name": "Commodities & Metals",
        "keywords": ["gold price", "silver", "copper", "commodity", "metals", "iron ore"],
        "description": "Commodity prices, precious metals, and raw materials",
    },
    "general-macro": {
        "name": "General Macro",
        "keywords": [],
        "description": "General macroeconomic news and analysis",
    },
}


def generate_slug(name):
    """Generate URL-safe slug from theme name."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')


def classify_article(article):
    """Classify an article into matching theme slugs."""
    text = f"{article.get('title', '')} {article.get('full_text', '')}".lower()
    matches = []

    for slug, theme in THEME_DEFINITIONS.items():
        if slug == "general-macro":
            continue
        if any(kw in text for kw in theme["keywords"]):
            matches.append(slug)

    if not matches:
        matches.append("general-macro")

    return matches


def cluster_articles():
    """Classify unassigned articles and assign them to themes."""
    # Fetch articles without a theme
    unassigned = execute_query(
        "SELECT id, title, full_text FROM articles WHERE theme_id IS NULL"
    )

    if not unassigned:
        logger.info("No unassigned articles to cluster")
        return 0

    logger.info(f"Clustering {len(unassigned)} unassigned articles")

    # Ensure all themes exist in DB first
    create_or_update_themes()

    # Get theme ID mapping
    themes = execute_query("SELECT id, slug FROM themes")
    slug_to_id = {t["slug"]: t["id"] for t in themes}

    # Classify and assign each article to its best match (first match)
    assigned = 0
    for article in unassigned:
        matches = classify_article(article)
        best_match = matches[0]
        theme_id = slug_to_id.get(best_match)

        if theme_id:
            try:
                execute_query(
                    "UPDATE articles SET theme_id = %s WHERE id = %s",
                    (theme_id, article["id"]),
                    fetch=False,
                )
                assigned += 1
            except Exception as e:
                logger.error(f"Error assigning article {article['id']}: {e}")

    logger.info(f"Assigned {assigned} articles to themes")
    return assigned


def create_or_update_themes():
    """Create or update theme records in the database."""
    for slug, definition in THEME_DEFINITIONS.items():
        try:
            execute_query(
                """
                INSERT INTO themes (name, slug, description, score_label, score_value, article_count, first_seen_at, last_updated_at)
                VALUES (%s, %s, %s, 'cool', 0, 0, NOW(), NOW())
                ON CONFLICT (slug) DO NOTHING
                """,
                (definition["name"], slug, definition["description"]),
                fetch=False,
            )
        except Exception as e:
            logger.error(f"Error creating theme '{slug}': {e}")


def calculate_temperatures():
    """Calculate temperature scores for all themes based on article count and recency."""
    themes = execute_query("SELECT id, slug FROM themes")

    for theme in themes:
        try:
            counts = execute_query(
                """
                SELECT
                    COUNT(*) FILTER (WHERE published_at >= NOW() - INTERVAL '24 hours') as last_24h,
                    COUNT(*) FILTER (WHERE published_at >= NOW() - INTERVAL '72 hours' AND published_at < NOW() - INTERVAL '24 hours') as last_72h,
                    COUNT(*) FILTER (WHERE published_at < NOW() - INTERVAL '72 hours') as older,
                    COUNT(*) as total
                FROM articles WHERE theme_id = %s
                """,
                (theme["id"],),
            )

            if not counts:
                continue

            c = counts[0]
            score_value = (c["last_24h"] * 3) + (c["last_72h"] * 1.5) + (c["older"] * 0.5)

            if score_value >= 10:
                score_label = "hot"
            elif score_value >= 4:
                score_label = "warm"
            else:
                score_label = "cool"

            execute_query(
                """
                UPDATE themes
                SET score_label = %s, score_value = %s, article_count = %s, last_updated_at = NOW()
                WHERE id = %s
                """,
                (score_label, score_value, c["total"], theme["id"]),
                fetch=False,
            )

        except Exception as e:
            logger.error(f"Error scoring theme {theme['slug']}: {e}")

    logger.info("Temperature scores updated for all themes")


def cache_themes():
    """Cache the full theme list in Redis."""
    themes = execute_query(
        """
        SELECT id, name, slug, description, score_label, score_value, article_count,
               region_tags, asset_tags, first_seen_at, last_updated_at
        FROM themes
        WHERE article_count > 0
        ORDER BY score_value DESC
        """
    )

    # Convert datetime objects for JSON serialization
    for t in themes:
        if t.get("first_seen_at"):
            t["first_seen_at"] = t["first_seen_at"].isoformat()
        if t.get("last_updated_at"):
            t["last_updated_at"] = t["last_updated_at"].isoformat()

    cache_set("macro:themes:all", themes, ttl=300)
    logger.info(f"Cached {len(themes)} themes to Redis")
    return themes


def snapshot_themes():
    """Save a daily snapshot of all themes to theme_history for institutional memory."""
    today = datetime.now(timezone.utc).date().isoformat()
    themes = execute_query("SELECT id, score_label, score_value, article_count, causal_chain FROM themes")

    saved = 0
    for t in themes:
        try:
            execute_query(
                """
                INSERT INTO theme_history (theme_id, snapshot_date, score_label, score_value, article_count, causal_chain)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (t["id"], today, t["score_label"], t["score_value"], t["article_count"], t["causal_chain"]),
                fetch=False,
            )
            saved += 1
        except Exception as e:
            logger.error(f"Error snapshotting theme {t['id']}: {e}")

    logger.info(f"Saved {saved} theme snapshots for {today}")
    return saved


def aggregate_theme_tags():
    """Roll up article-level region/asset tags to theme level.

    A theme gets a tag if 2+ of its articles carry that tag.
    """
    themes = execute_query("SELECT id FROM themes")

    for theme in themes:
        try:
            tag_data = execute_query(
                """
                SELECT
                    unnest(region_tags) as tag, 'region' as kind
                FROM articles WHERE theme_id = %s AND region_tags IS NOT NULL
                UNION ALL
                SELECT
                    unnest(asset_tags) as tag, 'asset' as kind
                FROM articles WHERE theme_id = %s AND asset_tags IS NOT NULL
                """,
                (theme["id"], theme["id"]),
            )

            # Count occurrences
            region_counts = {}
            asset_counts = {}
            for row in tag_data:
                if row["kind"] == "region":
                    region_counts[row["tag"]] = region_counts.get(row["tag"], 0) + 1
                else:
                    asset_counts[row["tag"]] = asset_counts.get(row["tag"], 0) + 1

            # Threshold: 2+ articles for a tag to apply to the theme
            region_tags = [t for t, c in region_counts.items() if c >= 2] or None
            asset_tags = [t for t, c in asset_counts.items() if c >= 2] or None

            execute_query(
                "UPDATE themes SET region_tags = %s, asset_tags = %s WHERE id = %s",
                (region_tags, asset_tags, theme["id"]),
                fetch=False,
            )
        except Exception as e:
            logger.error(f"Error aggregating tags for theme {theme['id']}: {e}")

    logger.info("Theme-level tags aggregated from articles")


def run_clustering():
    """Full clustering pipeline: classify, score, tag, snapshot, cache."""
    assigned = cluster_articles()
    calculate_temperatures()
    aggregate_theme_tags()
    snapshot_themes()
    themes = cache_themes()

    # Count themes with articles for NFR13 check
    active_themes = len(themes)
    logger.info(f"Active themes with articles: {active_themes}")

    return {
        "articles_assigned": assigned,
        "active_themes": active_themes,
        "themes": [{"name": t["name"], "score": t["score_label"], "articles": t["article_count"]} for t in themes],
    }
