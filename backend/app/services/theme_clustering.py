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
# Keywords are scored fallback only, used when Claude API is unavailable.
# Each keyword has a weight (2 = strong signal, 1 = supporting signal).
# exclude_keywords prevent false positives from overlapping themes.
THEME_DEFINITIONS = {
    "us-policy-regime-shift": {
        "name": "US Policy Regime Shift (Trump 2.0 / DOGE)",
        "keywords": [("doge government", 2), ("executive order", 2), ("government efficiency", 2), ("deregulation", 2), ("trump executive", 2), ("musk government", 2), ("trump deregulation", 2), ("federal workforce", 2), ("trump policy", 1)],
        "exclude_keywords": ["tariff on china", "china tariff", "chip ban", "export control"],
        "description": "Executive orders, deregulation, government efficiency initiatives — US domestic policy restructuring",
        "must_include": "US domestic policy actions: executive orders, DOGE, deregulation, government restructuring",
        "must_exclude": "China-specific tariffs (use us-china-tariffs), Fed rate decisions (use us-fed-rate-path)",
    },
    "us-china-tariffs-tech-decoupling": {
        "name": "US-China Tariffs & Tech Decoupling",
        "keywords": [("us china tariff", 2), ("trade war", 2), ("tech decoupling", 2), ("export control", 2), ("chip ban", 2), ("reshoring", 2), ("us china trade", 2), ("china tariff", 2), ("entity list", 2), ("trade deficit china", 1)],
        "exclude_keywords": ["executive order deregulation", "government efficiency", "doge"],
        "description": "Bilateral US-China tariffs, export controls, tech bans, supply chain reshoring",
        "must_include": "US-China bilateral trade/tech tensions: tariffs, chip bans, export controls, reshoring from China",
        "must_exclude": "Broad US domestic policy (use us-policy-regime-shift), China macro data (use china-economic-slowdown)",
    },
    "us-fed-rate-path": {
        "name": "US Fed Rate Path & Forward Guidance",
        "keywords": [("federal reserve", 2), ("fomc", 2), ("fed funds rate", 2), ("powell", 2), ("fed rate", 2), ("fed cut", 2), ("fed hike", 2), ("fed hold", 2), ("us interest rate", 2), ("fed governor", 1), ("fed chair", 1), ("federal open market", 2)],
        "exclude_keywords": ["ecb", "european central bank", "bank of england", "boe", "bank of japan", "boj", "rba", "reserve bank of australia", "pboc", "peoples bank", "rbnz", "bank of canada", "riksbank", "bank indonesia", "mas monetary"],
        "description": "US Federal Reserve rate decisions, FOMC statements, Fed forward guidance. EXCLUSIVELY the US Fed.",
        "must_include": "US Federal Reserve (Fed/FOMC/Powell) rate decisions, dot plots, forward guidance, QE/QT",
        "must_exclude": "ANY other central bank (ECB, BOE, BOJ, RBA, PBOC, MAS, etc.) — return null for those",
    },
    "europe-rearmament-defense": {
        "name": "Europe Rearmament & Defense Capex",
        "keywords": [("europe defense", 2), ("rearmament", 2), ("european defense", 2), ("defense budget europe", 2), ("nato spending", 2), ("military spending europe", 2), ("defense stock europe", 1), ("european military", 2)],
        "exclude_keywords": ["ukraine war frontline", "russia attack", "ceasefire"],
        "description": "European defense spending increases, NATO budget commitments, defense industrial stocks",
        "must_include": "European defense SPENDING/BUDGET/CAPEX increases, NATO financial commitments, defense industry",
        "must_exclude": "Russia-Ukraine war operations (use russia-ukraine-european-security)",
    },
    "ai-disruption-compute": {
        "name": "AI Disruption & Compute Infrastructure",
        "keywords": [("artificial intelligence", 2), ("ai model", 2), ("gpu demand", 2), ("data center", 2), ("nvidia", 2), ("ai regulation", 2), ("compute infrastructure", 2), ("machine learning", 1), ("large language model", 2), ("ai chip", 2)],
        "exclude_keywords": ["semiconductor supply chain", "rare earth", "chip shortage"],
        "description": "AI model advances, GPU/chip demand, data center buildout, AI regulation with macro implications",
        "must_include": "AI technology impact on markets/economy: model advances, compute demand, AI regulation, data center buildout",
        "must_exclude": "Semiconductor supply chains without AI angle (use critical-minerals-semiconductors), company product launches without macro angle",
    },
    "middle-east-conflict-energy": {
        "name": "Middle East Conflict & Energy Risk",
        "keywords": [("middle east conflict", 2), ("iran israel", 2), ("houthi", 2), ("strait of hormuz", 2), ("gaza", 2), ("red sea shipping", 2), ("oil supply risk", 2), ("iran nuclear", 2), ("hezbollah", 2), ("iran sanctions", 1)],
        "exclude_keywords": ["opec quota", "opec meeting", "production cut opec", "saudi production"],
        "description": "Geopolitical conflicts in Middle East causing energy supply disruption risk",
        "must_include": "Middle East CONFLICT/TENSION (Iran, Israel, Houthi, Red Sea) with energy supply risk angle",
        "must_exclude": "OPEC production management/quotas without conflict angle (use opec-oil-supply)",
    },
    "russia-ukraine-european-security": {
        "name": "Russia-Ukraine War & European Security",
        "keywords": [("russia ukraine", 2), ("ukraine war", 2), ("sanctions russia", 2), ("european energy security", 2), ("zelensky", 2), ("putin ukraine", 2), ("crimea", 2), ("ukraine frontline", 1), ("russian gas", 2)],
        "exclude_keywords": ["europe defense budget", "rearmament spending", "defense stock"],
        "description": "War developments, Russia sanctions, European energy security impacts",
        "must_include": "Russia-Ukraine WAR operations, sanctions on Russia, European energy security from Russian gas",
        "must_exclude": "European defense spending increases (use europe-rearmament-defense)",
    },
    "china-economic-slowdown": {
        "name": "China Economic Slowdown & Property Crisis",
        "keywords": [("china gdp", 2), ("china property crisis", 2), ("evergrande", 2), ("china deflation", 2), ("chinese economy slow", 2), ("country garden", 2), ("china consumer confidence", 2), ("china pmi", 2), ("china unemployment", 2), ("china housing", 1)],
        "exclude_keywords": ["pboc", "rrr cut", "rate cut", "stimulus package", "liquidity injection", "china easing", "taiwan strait", "south china sea"],
        "description": "China GDP weakness, property developer defaults, consumer confidence collapse, deflation data",
        "must_include": "China macro WEAKNESS data: GDP miss, property crisis, deflation, weak consumer/PMI — the PROBLEM",
        "must_exclude": "PBOC policy response (use china-pboc-stimulus), Taiwan/military tensions (use china-taiwan-indo-pacific)",
    },
    "china-pboc-stimulus": {
        "name": "China PBOC Stimulus & Monetary Easing",
        "keywords": [("pboc", 2), ("china rate cut", 2), ("rrr cut", 2), ("china stimulus", 2), ("china liquidity", 2), ("china fiscal stimulus", 2), ("china easing", 2), ("mlf rate", 2), ("lpr cut", 2), ("peoples bank of china", 2)],
        "exclude_keywords": ["china gdp miss", "china deflation data", "property default", "evergrande collapse", "taiwan", "south china sea"],
        "description": "PBOC rate cuts, RRR cuts, MLF/LPR adjustments, fiscal stimulus packages — the POLICY RESPONSE",
        "must_include": "PBOC or Chinese government POLICY ACTIONS: rate cuts, RRR, stimulus packages, liquidity injections",
        "must_exclude": "China macro weakness data (use china-economic-slowdown), military tensions (use china-taiwan-indo-pacific)",
    },
    "critical-minerals-semiconductors": {
        "name": "Critical Minerals & Semiconductor Supply",
        "keywords": [("semiconductor supply", 2), ("rare earth", 2), ("lithium supply", 2), ("chip shortage", 2), ("tsmc", 2), ("critical mineral", 2), ("cobalt", 2), ("chip supply chain", 2), ("semiconductor fabrication", 1)],
        "exclude_keywords": ["ai model", "large language model", "gpu demand ai", "data center ai"],
        "description": "Semiconductor fabrication supply chains, rare earth minerals, lithium, export restrictions on materials",
        "must_include": "SUPPLY CHAIN for chips/minerals: fabrication capacity, rare earth access, material export bans",
        "must_exclude": "AI demand for chips (use ai-disruption-compute), US-China chip bans (use us-china-tariffs if trade-focused)",
    },
    "global-sovereign-debt": {
        "name": "Global Sovereign Debt & Fiscal Sustainability",
        "keywords": [("sovereign debt", 2), ("fiscal deficit", 2), ("government debt gdp", 2), ("bond vigilante", 2), ("debt crisis", 2), ("debt ceiling", 2), ("fiscal sustainability", 2), ("national debt", 2), ("debt-to-gdp", 2)],
        "exclude_keywords": ["emerging market currency", "em crisis", "capital flight"],
        "description": "Government debt levels, fiscal deficits, bond market reactions, debt sustainability concerns",
        "must_include": "SOVEREIGN debt levels, fiscal deficit concerns, bond vigilantes, debt ceiling — developed or systemic",
        "must_exclude": "EM-specific currency/debt stress (use emerging-market-stress)",
    },
    "emerging-market-stress": {
        "name": "Emerging Market Currency & Debt Stress",
        "keywords": [("emerging market crisis", 2), ("em currency depreciation", 2), ("capital flight em", 2), ("dollar debt em", 2), ("frontier market", 2), ("em bond spread", 2), ("emerging market debt", 2), ("em capital outflow", 2)],
        "exclude_keywords": ["china gdp", "china property", "india gdp", "india growth", "pboc"],
        "description": "EM currency depreciation, dollar-denominated debt stress, capital flight from emerging markets",
        "must_include": "BROAD EM stress: currency depreciation, dollar debt burden, capital outflows from multiple EMs",
        "must_exclude": "China-specific issues (use china themes), India-specific growth (use india-growth-ascent)",
    },
    "india-growth-ascent": {
        "name": "India's Growth Ascent",
        "keywords": [("india gdp", 2), ("india growth", 2), ("india manufacturing", 2), ("modi reform", 2), ("india reform", 2), ("india market", 1), ("india demographic dividend", 2), ("make in india", 2), ("india infrastructure", 2)],
        "exclude_keywords": ["emerging market crisis", "em currency", "capital flight"],
        "description": "India GDP growth, manufacturing shift, demographic dividend, structural reforms",
        "must_include": "India GROWTH story: GDP expansion, manufacturing investment, reforms, demographic advantage",
        "must_exclude": "Broad EM stress that happens to include India (use emerging-market-stress)",
    },
    "opec-oil-supply": {
        "name": "OPEC+ Production & Oil Supply Politics",
        "keywords": [("opec", 2), ("opec production", 2), ("saudi oil production", 2), ("oil quota", 2), ("oil supply opec", 2), ("crude oil opec", 2), ("opec meeting", 2), ("production cut", 2), ("oil output", 1)],
        "exclude_keywords": ["iran israel", "houthi", "red sea", "gaza", "strait of hormuz", "middle east conflict"],
        "description": "OPEC+ production quotas, Saudi-Russia dynamics, coordinated oil supply management",
        "must_include": "OPEC+ PRODUCTION decisions: quotas, output cuts/increases, Saudi-Russia oil coordination",
        "must_exclude": "Middle East conflict causing oil risk (use middle-east-conflict-energy)",
    },
    "labor-immigration-demographics": {
        "name": "Labor Markets, Immigration & Demographics",
        "keywords": [("labor market", 2), ("wage growth", 2), ("labor shortage", 2), ("immigration policy", 2), ("aging population", 2), ("jobs report", 2), ("nonfarm payroll", 2), ("unemployment rate", 1), ("workforce participation", 2)],
        "exclude_keywords": [],
        "description": "Wage growth trends, labor shortages, immigration policy impact, aging population demographics",
        "must_include": "LABOR/DEMOGRAPHIC macro trends: wage data, employment reports, immigration policy, aging demographics",
        "must_exclude": "Individual company layoffs without macro angle",
    },
    "credit-shadow-banking": {
        "name": "Credit Conditions & Shadow Banking Risk",
        "keywords": [("credit spread", 2), ("private credit", 2), ("banking stress", 2), ("lending standard", 2), ("shadow banking", 2), ("credit crunch", 2), ("bank failure", 2), ("commercial real estate loan", 2), ("credit tightening", 2)],
        "exclude_keywords": [],
        "description": "Credit spreads, private credit growth, banking stress, lending standards tightening",
        "must_include": "CREDIT CONDITIONS: spreads, lending standards, banking stress, shadow banking, systemic credit risk",
        "must_exclude": "Sovereign debt (use global-sovereign-debt), individual bank earnings without systemic angle",
    },
    "nuclear-energy-renaissance": {
        "name": "Nuclear Energy Renaissance",
        "keywords": [("nuclear energy", 2), ("nuclear reactor", 2), ("small modular reactor", 2), ("uranium", 2), ("nuclear power plant", 2), ("nuclear policy", 2), ("smr", 2), ("nuclear renaissance", 2)],
        "exclude_keywords": ["nuclear weapon", "nuclear warhead", "iran nuclear deal"],
        "description": "New reactor builds, SMRs, nuclear policy shifts, uranium demand for energy",
        "must_include": "Nuclear ENERGY: reactor construction, SMR technology, nuclear policy for power generation, uranium demand",
        "must_exclude": "Nuclear weapons/proliferation, Iran nuclear deal (use middle-east-conflict-energy if conflict-related)",
    },
    "boj-yen-dynamics": {
        "name": "BOJ Policy Normalization & Yen Dynamics",
        "keywords": [("bank of japan", 2), ("boj rate", 2), ("yen carry trade", 2), ("yield curve control", 2), ("ueda", 2), ("japanese yen", 2), ("boj policy", 2), ("japan interest rate", 2), ("boj normalization", 2)],
        "exclude_keywords": ["federal reserve", "fomc", "powell", "ecb", "pboc"],
        "description": "BOJ rate decisions, yield curve control changes, yen carry trade dynamics",
        "must_include": "Bank of Japan POLICY: rate decisions, YCC changes, yen dynamics from BOJ actions",
        "must_exclude": "Other central banks (use their respective themes or return null)",
    },
    "de-dollarization": {
        "name": "De-dollarization & Reserve Currency Shifts",
        "keywords": [("de-dollarization", 2), ("brics currency", 2), ("gold reserve central bank", 2), ("yuan internationalization", 2), ("reserve currency shift", 2), ("dollar decline reserve", 2), ("brics payment", 2), ("dollar alternative", 2)],
        "exclude_keywords": [],
        "description": "BRICS currency alternatives, central bank gold accumulation, yuan internationalization",
        "must_include": "RESERVE CURRENCY dynamics: de-dollarization moves, BRICS alternatives, central bank gold buying",
        "must_exclude": "General dollar strength/weakness from Fed policy (use us-fed-rate-path)",
    },
    "china-taiwan-indo-pacific": {
        "name": "China-Taiwan Tensions & Indo-Pacific Security",
        "keywords": [("taiwan strait", 2), ("china taiwan", 2), ("indo-pacific", 2), ("south china sea", 2), ("aukus", 2), ("taiwan military", 2), ("taiwan semiconductor risk", 2), ("china military taiwan", 2), ("pla", 1)],
        "exclude_keywords": ["china gdp", "china property", "pboc", "china stimulus", "evergrande"],
        "description": "China-Taiwan military tensions, South China Sea, AUKUS, semiconductor supply risk from conflict",
        "must_include": "SECURITY/MILITARY tensions: Taiwan Strait, South China Sea, Indo-Pacific alliances, AUKUS",
        "must_exclude": "China economic data (use china-economic-slowdown), PBOC policy (use china-pboc-stimulus)",
    },
    "mas-sgd-policy": {
        "name": "MAS Policy & SGD Management",
        "keywords": [("monetary authority of singapore", 2), ("mas monetary policy", 2), ("mas policy", 2), ("sgd neer", 2), ("s$neer", 2), ("singapore dollar policy", 2), ("singapore exchange rate policy", 2), ("mas review", 2)],
        "exclude_keywords": ["singapore startup", "singapore property price", "singapore tourism"],
        "description": "MAS monetary policy decisions, S$NEER band adjustments, SGD management",
        "must_include": "MAS POLICY decisions: S$NEER band changes, monetary policy statements, exchange rate management",
        "must_exclude": "General Singapore economic data without MAS policy angle, Singapore business news",
    },
}


def generate_slug(name):
    """Generate URL-safe slug from theme name."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug.strip('-')


def _score_keyword_match(text, theme_def):
    """Score an article against a theme using weighted keywords and exclusions.

    Returns a score (0 if excluded or no match). Higher = stronger match.
    """
    # Check exclusion keywords first
    for ekw in theme_def.get("exclude_keywords", []):
        if ekw in text:
            return 0

    score = 0
    for kw, weight in theme_def["keywords"]:
        if kw in text:
            score += weight
    return score


def classify_article(article):
    """Classify an article into matching theme slugs.

    Uses Claude Sonnet first, falls back to scored keyword matching if Claude is unavailable.
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

    # Scored keyword fallback — requires minimum score of 4 (e.g., 2 strong keywords or 4 supporting)
    text = f"{title} {full_text}".lower()
    scored_matches = []
    for slug, theme in THEME_DEFINITIONS.items():
        score = _score_keyword_match(text, theme)
        if score >= 4:
            scored_matches.append((slug, score))

    if not scored_matches:
        return []

    # Return the highest-scoring theme
    scored_matches.sort(key=lambda x: x[1], reverse=True)
    best_slug = scored_matches[0][0]
    logger.info(f"Keyword fallback: '{title[:60]}' → {best_slug} (score={scored_matches[0][1]})")
    return [best_slug]


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
    # Use fixed reference date (last ingestion date) instead of real-time
    # to keep scores meaningful while news ingestion is paused.
    now = datetime(2025, 3, 10, 23, 59, 59, tzinfo=timezone.utc)

    # Single query for all recent articles across all themes
    articles = execute_query(
        """
        SELECT theme_id, published_at FROM articles
        WHERE published_at >= TIMESTAMP '2025-03-03 23:59:59 UTC'
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
