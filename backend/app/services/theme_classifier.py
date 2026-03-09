"""Claude-powered article classification for Watch List themes.

Classifies articles into one of 21 curated narrative themes using Claude Haiku,
with confidence threshold filtering. The 0.3s per-call rate-limit delay is handled
by the caller (cluster_articles loop). The 10s sleep on RateLimitError is an
error-recovery pause handled here.
"""
import json
import logging
import time

import anthropic

from app.utils.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-init Anthropic client."""
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _build_theme_list():
    """Build the theme list for the classification prompt from THEME_DEFINITIONS (single source of truth)."""
    from app.services.theme_clustering import THEME_DEFINITIONS
    lines = []
    for slug, defn in THEME_DEFINITIONS.items():
        lines.append(f"- {slug}: {defn['name']} — {defn['description']}")
    return "\n".join(lines)


def _build_prompt():
    """Build the classification prompt with the current theme list."""
    theme_list = _build_theme_list()
    return f"""You are a financial news classifier. Classify this article into exactly one of these macro narrative themes, or none if it doesn't fit.

Themes:
{theme_list}

Return ONLY valid JSON: {{"theme_slug": "<slug>", "confidence": 0.0-1.0}}
If no theme fits, return: {{"theme_slug": null, "confidence": 0.0}}"""


def _get_valid_slugs():
    """Get the set of valid theme slugs from THEME_DEFINITIONS."""
    from app.services.theme_clustering import THEME_DEFINITIONS
    return set(THEME_DEFINITIONS.keys())


CONFIDENCE_THRESHOLD = 0.5


def classify_article_with_claude(title, text):
    """Classify an article into a theme slug using Claude Haiku.

    Returns theme slug string or None. Rate-limit delay is handled by caller.
    """
    client = _get_client()
    if not client:
        return None

    prompt = _build_prompt()
    valid_slugs = _get_valid_slugs()
    user_msg = f"Title: {title}\nText: {(text or '')[:1000]}"

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n{user_msg}"}
            ],
        )
        if not response.content:
            return None
        raw = response.content[0].text.strip()

        # Extract JSON object from response — Claude may wrap in code fences or add extra text
        import re
        json_match = re.search(r'\{[^}]+\}', raw)
        if not json_match:
            logger.warning(f"No JSON object found in Claude response: {raw[:100]}")
            return None
        raw = json_match.group()

        # Parse JSON response
        result = json.loads(raw)
        slug = result.get("theme_slug")
        confidence = result.get("confidence", 0.0)

        if slug and confidence >= CONFIDENCE_THRESHOLD:
            if slug not in valid_slugs:
                logger.warning(f"Claude returned invalid slug '{slug}', ignoring")
                return None
            return slug
        return None

    except anthropic.RateLimitError:
        logger.warning("Claude API rate limit hit during classification, pausing 10s")
        time.sleep(10)
        return None
    except anthropic.APITimeoutError:
        logger.warning("Claude API timeout during classification")
        return None
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Failed to parse Claude classification response: {e}")
        return None
    except Exception as e:
        logger.error(f"Claude classification error: {e}")
        return None
