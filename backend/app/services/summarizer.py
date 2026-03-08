"""AI article summarization via Claude API (Story 2.3).

Based on Person 3's ai/article_summarizer.py, adapted to use Claude API
with one-line summaries, rate limiting, and graceful error handling.
"""
import logging
import time

import anthropic

from app.models.db import execute_query
from app.utils.cache import cache_get, cache_set
from app.utils.config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-init Anthropic client."""
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def generate_summary(title, text):
    """Generate a one-line summary (max 30 words) for an article.

    Returns summary string or None on failure.
    """
    client = _get_client()
    if not client:
        return None

    # Check Redis cache first
    cache_key = f"macro:summary:{hash(title)}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    # Skip if no meaningful text to summarize
    if len(text.strip()) < 20:
        return None

    prompt = (
        "Summarize this macroeconomic news article in exactly one sentence, "
        "maximum 30 words. Focus on the key takeaway for an asset manager. "
        "Do not include any preamble.\n\n"
        f"Title: {title}\n"
        f"Text: {text[:1000]}"
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response.content[0].text.strip()

        # Cache for 24 hours
        cache_set(cache_key, summary, ttl=86400)
        return summary

    except anthropic.RateLimitError:
        logger.warning("Claude API rate limit hit, pausing 10s")
        time.sleep(10)
        return None
    except anthropic.APITimeoutError:
        logger.warning("Claude API timeout")
        return None
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return None


def summarize_unsummarized(batch_size=20):
    """Summarize articles that don't have an ai_summary yet.

    Processes in batches with a small delay to respect rate limits.
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, skipping summarization")
        return 0

    articles = execute_query(
        """
        SELECT id, title, full_text
        FROM articles
        WHERE ai_summary IS NULL
        ORDER BY published_at DESC
        LIMIT %s
        """,
        (batch_size,),
    )

    if not articles:
        logger.info("No articles need summarization")
        return 0

    logger.info(f"Summarizing {len(articles)} articles...")
    summarized = 0

    for article in articles:
        title = article.get("title", "")
        text = article.get("full_text", "") or title

        summary = generate_summary(title, text)
        if summary:
            try:
                execute_query(
                    "UPDATE articles SET ai_summary = %s WHERE id = %s",
                    (summary, article["id"]),
                    fetch=False,
                )
                summarized += 1
            except Exception as e:
                logger.error(f"Error saving summary for article {article['id']}: {e}")

        # Small delay between API calls to respect rate limits
        time.sleep(0.5)

    logger.info(f"Summarized {summarized}/{len(articles)} articles")
    return summarized
