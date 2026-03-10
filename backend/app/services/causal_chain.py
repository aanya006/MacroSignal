"""Causal chain generation for hot themes via Claude API (Story 3.1).

Generates structured causal chains showing:
Trigger → Mechanism → per-asset-class impacts (Equities, Bonds, FX, Commodities)
"""
import json
import logging
from datetime import datetime, timezone

import anthropic

from app.models.db import execute_query
from app.utils.cache import cache_get, cache_set
from app.utils.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = None

CAUSAL_CHAIN_PROMPT = """You are a senior macro strategist writing a concise market intelligence brief for an experienced buy-side asset manager. Your audience actively manages multi-asset portfolios and expects precise, professional analysis — not simplified explanations.

Theme: {theme_name}
Description: {theme_description}

Recent articles:
{articles_context}

Generate a causal chain analysis grounded in the specific developments described in the articles above. Do not produce generic textbook reasoning — every sentence must reflect what is actually happening in the news provided.

Respond with ONLY valid JSON in this exact format (no markdown, no code fences):
{{
  "trigger": "One sentence identifying the specific macro catalyst or policy shift, using precise terminology (e.g. rate differentials, yield curve dynamics, fiscal expansion)",
  "mechanism": "One sentence explaining the exact transmission pathway through financial markets — name the mechanism (e.g. risk-off rotation, dollar funding squeeze, commodity supply shock, capital flow reversal)",
  "impacts": {{
    "equities": {{"direction": "positive|negative|neutral", "summary": "One to two sentences on equity market impact — specify sectors, indices, or valuation dynamics affected; reference Asia/Singapore where relevant"}},
    "bonds": {{"direction": "positive|negative|neutral", "summary": "One to two sentences on fixed income impact — reference duration, credit spreads, sovereign vs corporate, or yield curve implications"}},
    "fx": {{"direction": "positive|negative|neutral", "summary": "One to two sentences on currency dynamics — name specific pairs or EM currency baskets; reference SGD or Asian FX where applicable"}},
    "commodities": {{"direction": "positive|negative|neutral", "summary": "One to two sentences on commodity market impact — specify the relevant commodity class and supply/demand or geopolitical driver"}}
  }}
}}

Rules:
- Write for a CFA-level reader — use standard financial terminology without explanation
- Be specific: reference actual market mechanisms, not generic cause-effect
- Direction must be exactly "positive", "negative", or "neutral"
- Each impact summary is one to two sentences maximum
- Ground every claim in the article context provided — avoid boilerplate
- Reference Singapore or Asian market implications where naturally relevant, but do not force it"""


def _get_client():
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def generate_causal_chain(theme):
    """Generate a causal chain for a single theme.

    Args:
        theme: dict with id, name, slug, description

    Returns:
        dict (parsed causal chain) or None on failure
    """
    client = _get_client()
    if not client:
        logger.warning("No Anthropic client available, skipping causal chain")
        return None

    # Check Redis cache first
    cache_key = f"macro:causal:{theme['slug']}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    # Get recent articles for context
    articles = execute_query(
        """
        SELECT title, ai_summary
        FROM articles
        WHERE theme_id = %s AND published_at IS NOT NULL
        ORDER BY published_at DESC
        LIMIT 10
        """,
        (theme["id"],),
    )

    articles_context = "\n".join(
        f"- {a['title']}" + (f" — {a['ai_summary']}" if a.get("ai_summary") else "")
        for a in articles
    )

    if not articles_context:
        logger.info(f"No articles for theme {theme['slug']}, skipping causal chain")
        return None

    prompt = CAUSAL_CHAIN_PROMPT.format(
        theme_name=theme["name"],
        theme_description=theme.get("description", ""),
        articles_context=articles_context,
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3].strip()

        # Parse JSON response
        chain = json.loads(raw)

        # Validate structure
        if not all(k in chain for k in ("trigger", "mechanism", "impacts")):
            logger.error(f"Invalid causal chain structure for {theme['slug']}")
            return None

        # Cache for 2 hours
        cache_set(cache_key, chain, ttl=7200)

        # Store in DB
        execute_query(
            """
            UPDATE themes
            SET causal_chain = %s, causal_chain_generated_at = %s
            WHERE id = %s
            """,
            (json.dumps(chain), datetime.now(timezone.utc), theme["id"]),
            fetch=False,
        )

        logger.info(f"Generated causal chain for {theme['slug']}")
        return chain

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse causal chain JSON for {theme['slug']}: {e}")
        return None
    except anthropic.RateLimitError:
        logger.warning("Claude API rate limit hit during causal chain generation")
        return None
    except anthropic.APITimeoutError:
        logger.warning("Claude API timeout during causal chain generation")
        return None
    except Exception as e:
        logger.error(f"Causal chain generation error for {theme['slug']}: {e}")
        return None


def generate_chains_for_hot_themes():
    """Generate causal chains for all hot themes that need one.

    Skips themes that already have a recent chain (< 2 hours old).
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, skipping causal chain generation")
        return 0

    hot_themes = execute_query(
        """
        SELECT id, name, slug, description, causal_chain_generated_at
        FROM themes
        WHERE score_label = 'hot'
        """,
    )

    if not hot_themes:
        logger.info("No hot themes for causal chain generation")
        return 0

    generated = 0
    now = datetime.now(timezone.utc)

    for theme in hot_themes:
        # Skip catch-all theme — not a meaningful macro signal
        if theme["slug"] == "general-macro":
            continue

        # Skip if chain was generated recently (< 2 hours)
        gen_at = theme.get("causal_chain_generated_at")
        if gen_at:
            if hasattr(gen_at, "tzinfo") and gen_at.tzinfo is None:
                gen_at = gen_at.replace(tzinfo=timezone.utc)
            age_seconds = (now - gen_at).total_seconds()
            if age_seconds < 7200:
                logger.info(f"Skipping {theme['slug']} — chain is {age_seconds/60:.0f}min old")
                continue

        chain = generate_causal_chain(theme)
        if chain:
            generated += 1

    logger.info(f"Generated {generated} causal chains for hot themes")
    return generated
