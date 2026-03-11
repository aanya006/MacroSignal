import json
import logging
import math
import re
import time
from datetime import datetime, timezone

from app.models.db import execute_query, get_connection, release_connection
from app.utils.cache import cache_set

logger = logging.getLogger(__name__)

# 21 curated narrative themes — Watch List
# Keywords are broad fallback only, used when Claude API is unavailable
THEME_DEFINITIONS = {
    "us-policy-regime-shift": {
        "name": "US Policy Regime Shift (Trump 2.0 / DOGE)",
        "keywords": ["trump", "doge", "executive order", "deregulation", "government efficiency", "musk", "tariff executive"],
        "description": "Executive orders, deregulation, government efficiency initiatives",
    },
    "us-china-tariffs-tech-decoupling": {
        "name": "US-China Tariffs & Tech Decoupling",
        "keywords": ["us china tariff", "trade war", "tech decoupling", "export control", "chip ban", "reshoring", "us china trade"],
        "description": "Bilateral tariffs, export controls, tech bans, supply chain reshoring",
    },
    "us-fed-rate-path": {
        "name": "US Fed Rate Path & Forward Guidance",
        "keywords": ["federal reserve", "fed rate", "fomc", "powell", "fed funds", "rate cut", "rate hike", "fed policy"],
        "description": "Federal Reserve rate decisions, FOMC statements, inflation targeting",
    },
    "europe-rearmament-defense": {
        "name": "Europe Rearmament & Defense Capex",
        "keywords": ["europe defense", "nato spending", "rearmament", "defense budget", "european defense", "defense stock", "military spending europe"],
        "description": "European defense spending increases, NATO commitments, defense stocks",
    },
    "ai-disruption-compute": {
        "name": "AI Disruption & Compute Infrastructure",
        "keywords": ["artificial intelligence", "ai model", "gpu", "data center", "nvidia", "ai regulation", "compute", "machine learning"],
        "description": "AI model advances, GPU/chip demand, data center buildout, AI regulation",
    },
    "middle-east-conflict-energy": {
        "name": "Middle East Conflict & Energy Risk",
        "keywords": ["middle east conflict", "iran", "israel", "houthi", "strait of hormuz", "gaza", "oil supply risk", "red sea"],
        "description": "Regional conflicts affecting oil supply, Strait of Hormuz, energy prices",
    },
    "russia-ukraine-european-security": {
        "name": "Russia-Ukraine War & European Security",
        "keywords": ["russia ukraine", "ukraine war", "sanctions russia", "european energy", "nato", "zelensky", "putin"],
        "description": "War developments, sanctions, European energy security, NATO",
    },
    "china-economic-slowdown": {
        "name": "China Economic Slowdown & Property Crisis",
        "keywords": ["china gdp", "china property", "evergrande", "china deflation", "chinese economy", "country garden", "china consumer"],
        "description": "GDP growth, property developer defaults, consumer confidence, deflation",
    },
    "china-pboc-stimulus": {
        "name": "China PBOC Stimulus & Monetary Easing",
        "keywords": ["pboc", "china rate cut", "rrr cut", "china stimulus", "china liquidity", "china fiscal", "china easing"],
        "description": "Rate cuts, RRR cuts, liquidity injections, fiscal stimulus packages",
    },
    "critical-minerals-semiconductors": {
        "name": "Critical Minerals & Semiconductor Supply",
        "keywords": ["semiconductor supply", "rare earth", "lithium", "chip shortage", "tsmc", "critical mineral", "cobalt"],
        "description": "Chip supply chains, rare earths, lithium, export restrictions",
    },
    "global-sovereign-debt": {
        "name": "Global Sovereign Debt & Fiscal Sustainability",
        "keywords": ["sovereign debt", "fiscal deficit", "government debt", "bond vigilante", "debt crisis", "debt ceiling", "fiscal sustainability"],
        "description": "Government debt levels, fiscal deficits, bond vigilantes, debt crises",
    },
    "emerging-market-stress": {
        "name": "Emerging Market Currency & Debt Stress",
        "keywords": ["emerging market", "em currency", "capital flight", "dollar debt", "em crisis", "frontier market", "em bond"],
        "description": "EM currency depreciation, dollar-denominated debt, capital flight",
    },
    "india-growth-ascent": {
        "name": "India's Growth Ascent",
        "keywords": ["india gdp", "india growth", "india manufacturing", "modi", "india reform", "india market", "india demographic"],
        "description": "GDP growth, manufacturing shift, demographic dividend, market reforms",
    },
    "opec-oil-supply": {
        "name": "OPEC+ Production & Oil Supply Politics",
        "keywords": ["opec", "oil production", "saudi oil", "oil quota", "oil price", "crude oil", "brent", "oil supply"],
        "description": "Production quotas, Saudi-Russia dynamics, oil price management",
    },
    "labor-immigration-demographics": {
        "name": "Labor Markets, Immigration & Demographics",
        "keywords": ["labor market", "wage growth", "labor shortage", "immigration policy", "aging population", "unemployment", "jobs report"],
        "description": "Wage growth, labor shortages, immigration policy, aging populations",
    },
    "credit-shadow-banking": {
        "name": "Credit Conditions & Shadow Banking Risk",
        "keywords": ["credit spread", "private credit", "banking stress", "lending standard", "shadow banking", "credit crunch", "bank failure"],
        "description": "Credit spreads, private credit, banking stress, lending standards",
    },
    "nuclear-energy-renaissance": {
        "name": "Nuclear Energy Renaissance",
        "keywords": ["nuclear energy", "nuclear reactor", "smr", "uranium", "nuclear power", "nuclear policy", "small modular reactor"],
        "description": "New reactor builds, SMRs, nuclear policy shifts, uranium demand",
    },
    "boj-yen-dynamics": {
        "name": "BOJ Policy Normalization & Yen Dynamics",
        "keywords": ["boj", "bank of japan", "yen", "yield curve control", "ueda", "japanese yen", "yen carry trade"],
        "description": "Rate hikes, yield curve control changes, yen carry trade",
    },
    "de-dollarization": {
        "name": "De-dollarization & Reserve Currency Shifts",
        "keywords": ["de-dollarization", "brics currency", "gold reserve", "yuan internationalization", "reserve currency", "dollar decline"],
        "description": "BRICS alternatives, gold reserves, yuan internationalization",
    },
    "china-taiwan-indo-pacific": {
        "name": "China-Taiwan Tensions & Indo-Pacific Security",
        "keywords": ["taiwan", "china taiwan", "indo-pacific", "south china sea", "aukus", "taiwan strait", "taiwan semiconductor"],
        "description": "Military posturing, semiconductor supply risk, alliance dynamics",
    },
    "mas-sgd-policy": {
        "name": "MAS Policy & SGD Management",
        "keywords": ["monetary authority of singapore", "mas monetary policy", "mas policy", "sgd neer", "s$neer", "singapore dollar policy", "singapore exchange rate policy"],
        "description": "Singapore monetary policy, S$NEER band adjustments, regional FX impact",
    },
}


def generate_slug(name):
    """Generate URL-safe slug from theme name."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')


def classify_article(article):
    """Classify an article into matching theme slugs.

    Uses Claude Haiku first, falls back to keyword matching if Claude is unavailable.
    Returns list of slug strings (0 or 1 items).
    """
    title = article.get("title", "")
    full_text = article.get("full_text", "")

    # Try Claude classification first
    try:
        from app.services.theme_classifier import classify_article_with_claude
        slug = classify_article_with_claude(title, full_text)
        if slug:
            return [slug]
    except Exception as e:
        logger.warning(f"Claude classification failed, falling back to keywords: {e}")

    # Keyword fallback
    text = f"{title} {full_text}".lower()
    matches = []
    for slug, theme in THEME_DEFINITIONS.items():
        if any(kw in text for kw in theme["keywords"]):
            matches.append(slug)

    return matches[:1] if matches else []


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

    # Classify and assign each article to its best match
    assigned = 0
    for article in unassigned:
        matches = classify_article(article)

        if not matches:
            continue

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

        # Rate-limit delay only when Claude API is active
        from app.utils.config import ANTHROPIC_API_KEY
        if ANTHROPIC_API_KEY:
            time.sleep(0.3)

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
                ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name, description = EXCLUDED.description
                """,
                (definition["name"], slug, definition["description"]),
                fetch=False,
            )
        except Exception as e:
            logger.error(f"Error creating theme '{slug}': {e}")


# 24-hour half-life: score = Σ exp(-λ * age_hours) for articles in last 7 days.
# Each article contributes at most 1.0 (just published), decaying to 0.5 at 24h, 0.25 at 48h, etc.
_DECAY_HALF_LIFE_HOURS = 24
_DECAY_LAMBDA = math.log(2) / _DECAY_HALF_LIFE_HOURS
_HOT_THRESHOLD = 3.0   # ~3+ fresh articles in last 24h
_WARM_THRESHOLD = 1.0  # ~1-2 fresh articles


def calculate_temperatures():
    """Calculate temperature scores for all themes using exponential decay.

    Score = Σ exp(-λ * age_hours) for articles published in the last 7 days,
    where λ = ln(2) / 24 gives a 24-hour half-life. Articles older than 7 days
    contribute < 0.008 each and are ignored.
    """
    now = datetime.now(timezone.utc)

    # Single query for all recent articles across all themes
    articles = execute_query(
        """
        SELECT theme_id, published_at FROM articles
        WHERE published_at >= NOW() - INTERVAL '7 days'
        AND theme_id IS NOT NULL
        """
    )

    # Total article counts per theme (all time, for article_count column)
    total_counts = execute_query(
        "SELECT theme_id, COUNT(*) as total FROM articles WHERE theme_id IS NOT NULL GROUP BY theme_id"
    )
    total_by_theme = {r["theme_id"]: r["total"] for r in total_counts}

    # Compute decay scores in Python
    scores = {}
    for a in articles:
        tid = a["theme_id"]
        pub = a["published_at"]
        # Normalize to tz-aware if DB returns naive datetimes
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        age_hours = (now - pub).total_seconds() / 3600
        scores[tid] = scores.get(tid, 0.0) + math.exp(-_DECAY_LAMBDA * age_hours)

    themes = execute_query("SELECT id, slug FROM themes")
    for theme in themes:
        tid = theme["id"]
        score_value = round(scores.get(tid, 0.0), 4)
        total = total_by_theme.get(tid, 0)

        if score_value >= _HOT_THRESHOLD:
            score_label = "hot"
        elif score_value >= _WARM_THRESHOLD:
            score_label = "warm"
        else:
            score_label = "cool"

        try:
            execute_query(
                """
                UPDATE themes
                SET score_label = %s, score_value = %s, article_count = %s, last_updated_at = NOW()
                WHERE id = %s
                """,
                (score_label, score_value, total, theme["id"]),
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
        WHERE article_count > 0 AND (is_historical = FALSE OR is_historical IS NULL)
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


def reclassify_theme(target_slug):
    """Reclassify only articles currently assigned to a specific theme.

    Unlinks those articles, reclassifies them (they may land in a different
    theme, the same theme, or no theme), then refreshes scores and caches.
    """
    logger.info(f"Starting targeted reclassification for theme '{target_slug}'")

    # Get the theme ID
    theme_rows = execute_query(
        "SELECT id FROM themes WHERE slug = %s", (target_slug,)
    )
    if not theme_rows:
        raise ValueError(f"Theme '{target_slug}' not found")

    theme_id = theme_rows[0]["id"]

    # Count affected articles
    count_rows = execute_query(
        "SELECT COUNT(*) as cnt FROM articles WHERE theme_id = %s", (theme_id,)
    )
    article_count = count_rows[0]["cnt"] if count_rows else 0
    logger.info(f"Unlinking {article_count} articles from '{target_slug}'")

    # Unlink articles from this theme
    execute_query(
        "UPDATE articles SET theme_id = NULL WHERE theme_id = %s",
        (theme_id,),
        fetch=False,
    )

    # Clear the theme's causal chain so it regenerates fresh
    execute_query(
        "UPDATE themes SET causal_chain = NULL, causal_chain_generated_at = NULL, "
        "article_count = 0, score_value = 0, score_label = 'cool' WHERE id = %s",
        (theme_id,),
        fetch=False,
    )

    # Reclassify just the unlinked articles (now theme_id IS NULL)
    assigned = cluster_articles()
    calculate_temperatures()
    aggregate_theme_tags()

    # Regenerate causal chains for hot themes
    try:
        from app.services.causal_chain import generate_chains_for_hot_themes
        generate_chains_for_hot_themes()
    except Exception as e:
        logger.error(f"Causal chain generation error during reclassification: {e}")

    snapshot_themes()
    themes = cache_themes()

    logger.info(f"Targeted reclassification complete for '{target_slug}': "
                f"{article_count} articles unlinked, {assigned} reassigned")
    return {
        "target_theme": target_slug,
        "articles_unlinked": article_count,
        "articles_reassigned": assigned,
        "active_themes": len(themes),
    }


def reclassify_all_articles():
    """Wipe all theme assignments and reclassify everything against the new 21 themes.

    Uses a single transaction for the wipe phase (steps 1-3) since execute_query()
    auto-commits per call on separate connections and cannot do multi-statement transactions.
    """
    logger.info("Starting full reclassification...")

    # Wipe phase — single transaction via raw connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE articles SET theme_id = NULL")
            cur.execute("DELETE FROM theme_history WHERE theme_id IN (SELECT id FROM themes)")
            cur.execute("DELETE FROM themes")
        conn.commit()
        logger.info("Wipe phase complete: articles unlinked, theme_history and themes deleted")
    except Exception:
        conn.rollback()
        logger.error("Wipe phase failed, rolling back")
        raise
    finally:
        release_connection(conn)

    # Rebuild phase — normal execute_query() calls
    assigned = cluster_articles()
    calculate_temperatures()
    aggregate_theme_tags()

    # Generate causal chains for hot themes
    try:
        from app.services.causal_chain import generate_chains_for_hot_themes
        generate_chains_for_hot_themes()
    except Exception as e:
        logger.error(f"Causal chain generation error during reclassification: {e}")

    snapshot_themes()
    themes = cache_themes()

    logger.info(f"Reclassification complete: {assigned} articles assigned to {len(themes)} themes")
    return {
        "articles_assigned": assigned,
        "themes_created": len(themes),
        "themes": [{"name": t["name"], "score": t["score_label"], "articles": t["article_count"]} for t in themes],
    }


def run_clustering():
    """Full clustering pipeline: classify, score, tag, causal chains, snapshot, cache."""
    assigned = cluster_articles()
    calculate_temperatures()
    aggregate_theme_tags()

    # Generate causal chains for hot themes
    try:
        from app.services.causal_chain import generate_chains_for_hot_themes
        generate_chains_for_hot_themes()
    except Exception as e:
        logger.error(f"Causal chain generation error: {e}")

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
