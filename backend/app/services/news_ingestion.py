import os
import logging
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import quote

import requests

from app.models.db import execute_query, execute_many
from app.services.tagging import classify_tags
from app.utils.config import NEWS_API_KEY

logger = logging.getLogger(__name__)

# Financial and macroeconomic keywords for filtering
FINANCIAL_KEYWORDS = [
    "inflation", "interest rate", "gdp", "central bank", "monetary policy",
    "tariff", "trade war", "recession", "bond yield", "currency", "forex",
    "equity", "commodity", "oil price", "fed", "federal reserve", "fomc",
    "mas", "ecb", "boj", "pboc", "fiscal policy", "debt", "deficit",
    "employment", "pmi", "cpi", "manufacturing", "rate cut", "rate hike",
    "quantitative", "stimulus", "sanctions", "geopolitical",
    "semiconductor", "treasury", "sovereign", "emerging market",
    "asean", "singapore", "china economy", "yuan", "sgd", "neer",
]

# Priority sources for Singapore/Asia focus
PRIORITY_SOURCES = [
    "CNA", "Channel NewsAsia", "Business Times", "Straits Times",
    "Reuters", "Bloomberg", "MAS", "Nikkei Asia",
]


_OG_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

_OG_PATTERNS = [
    re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', re.IGNORECASE),
    re.compile(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']', re.IGNORECASE),
]


def scrape_og_image(url):
    """Fetch article URL and extract og:image / twitter:image meta tag."""
    if not url:
        return None
    try:
        resp = requests.get(url, headers=_OG_HEADERS, timeout=8, allow_redirects=True)
        if resp.status_code != 200:
            return None
        # Only look in the first 20 KB — the <head> is always near the top
        head_chunk = resp.text[:20000]
        for pattern in _OG_PATTERNS:
            m = pattern.search(head_chunk)
            if m:
                img = m.group(1).strip()
                if img.startswith("http"):
                    return img
    except Exception:
        pass
    return None


def enrich_with_og_images(articles, max_workers=6):
    """Scrape og:image for articles that have no image_url, in parallel."""
    to_scrape = [a for a in articles if not a.get("image_url")]
    if not to_scrape:
        return

    logger.info(f"Scraping OG images for {len(to_scrape)} articles...")
    fetched = 0

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(scrape_og_image, a["url"]): a for a in to_scrape}
        for future in as_completed(futures):
            article = futures[future]
            try:
                img = future.result()
                if img:
                    article["image_url"] = img
                    fetched += 1
            except Exception as e:
                logger.debug(f"OG scrape error for {article.get('url', '')[:60]}: {e}")

    logger.info(f"OG image scraping complete: {fetched}/{len(to_scrape)} found")


def backfill_tags(batch_size=1000):
    """Re-run classify_tags on all existing articles and update region/asset tags in DB."""
    rows = execute_query(
        "SELECT id, title, full_text FROM articles ORDER BY ingested_at DESC LIMIT %s",
        (batch_size,),
    )
    if not rows:
        logger.info("backfill_tags: no articles found")
        return {"updated": 0, "total": 0}

    logger.info(f"backfill_tags: re-tagging {len(rows)} articles...")
    updated = 0

    for row in rows:
        try:
            text = f"{row['title'] or ''} {row['full_text'] or ''}"
            regions, assets = classify_tags(text)
            execute_query(
                "UPDATE articles SET region_tags = %s, asset_tags = %s WHERE id = %s",
                (regions or None, assets or None, row["id"]),
                fetch=False,
            )
            updated += 1
        except Exception as e:
            logger.error(f"backfill_tags error for id={row['id']}: {e}")

    logger.info(f"backfill_tags: updated {updated}/{len(rows)} articles")
    return {"updated": updated, "total": len(rows)}


def backfill_og_images(batch_size=100, max_workers=6):
    """Scrape og:image for existing DB articles that have no image_url."""
    rows = execute_query(
        "SELECT id, url FROM articles WHERE image_url IS NULL OR image_url = '' ORDER BY published_at DESC LIMIT %s",
        (batch_size,),
    )
    if not rows:
        logger.info("backfill_og_images: no articles need backfilling")
        return {"backfilled": 0, "total": 0}

    logger.info(f"backfill_og_images: scraping {len(rows)} articles...")
    updated = 0

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(scrape_og_image, row["url"]): row for row in rows}
        for future in as_completed(futures):
            row = futures[future]
            try:
                img = future.result()
                if img:
                    execute_query(
                        "UPDATE articles SET image_url = %s WHERE id = %s AND (image_url IS NULL OR image_url = '')",
                        (img, row["id"]),
                        fetch=False,
                    )
                    updated += 1
            except Exception as e:
                logger.debug(f"backfill error for id={row['id']}: {e}")

    logger.info(f"backfill_og_images: updated {updated}/{len(rows)}")
    return {"backfilled": updated, "total": len(rows)}


def is_relevant(article):
    """Check if article matches financial keywords."""
    text = f"{article.get('title', '')} {article.get('description', '')} {article.get('full_text', '')}".lower()
    return any(kw in text for kw in FINANCIAL_KEYWORDS)


def fetch_from_newsapi():
    """Fetch articles from NewsAPI free tier."""
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set, skipping NewsAPI")
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "macroeconomic OR monetary policy OR central bank OR inflation OR interest rate",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 50,
    }
    headers = {"X-Api-Key": NEWS_API_KEY}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 429:
            logger.warning("NewsAPI rate limit exceeded (429)")
            return []
        if resp.status_code == 401:
            logger.warning("NewsAPI authentication failed (401)")
            return []
        resp.raise_for_status()

        data = resp.json()
        articles = []
        for item in data.get("articles", []):
            if item.get("title") == "[Removed]":
                continue
            articles.append({
                "title": item.get("title", ""),
                "source_name": item.get("source", {}).get("name", "Unknown"),
                "url": item.get("url", ""),
                "published_at": item.get("publishedAt"),
                "full_text": item.get("content") or item.get("description") or "",
                "description": item.get("description") or "",
                "image_url": item.get("urlToImage") or "",
            })
        logger.info(f"NewsAPI returned {len(articles)} articles")
        return articles

    except requests.RequestException as e:
        logger.error(f"NewsAPI error: {e}")
        return []


def fetch_from_google_rss():
    """Fetch articles from Google News RSS (no API key needed)."""
    queries = [
        "macroeconomic policy",
        "central bank interest rate",
        "Singapore MAS monetary policy",
    ]
    all_articles = []

    for query in queries:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-SG&gl=SG&ceid=SG:en"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()

            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue

            for item in channel.findall("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                source = item.findtext("source", "Google News")
                description = item.findtext("description", "")

                # Parse RSS date format
                parsed_date = None
                if pub_date:
                    try:
                        parsed_date = datetime.strptime(
                            pub_date, "%a, %d %b %Y %H:%M:%S %Z"
                        ).replace(tzinfo=timezone.utc).isoformat()
                    except ValueError:
                        parsed_date = datetime.now(timezone.utc).isoformat()

                all_articles.append({
                    "title": title,
                    "source_name": source if source else "Google News",
                    "url": link,
                    "published_at": parsed_date,
                    "full_text": description,
                    "description": description,
                })

        except requests.RequestException as e:
            logger.error(f"Google RSS error for query '{query}': {e}")
            continue
        except ET.ParseError as e:
            logger.error(f"Google RSS XML parse error: {e}")
            continue

    logger.info(f"Google RSS returned {len(all_articles)} articles")
    return all_articles


_MEDIA_NS = "http://search.yahoo.com/mrss/"

# Direct source RSS feeds — give real article URLs and often include images
DIRECT_RSS_FEEDS = [
    # CNA: real URLs + media:thumbnail images
    ("CNA", "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6936"),
    ("CNA", "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6311"),
    # CNBC: real URLs, og:image scrapable
    ("CNBC", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
    ("CNBC", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
    # Yahoo Finance: real publisher URLs (WSJ, Bloomberg, etc.)
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
]


def _parse_rss_date(pub_date):
    if not pub_date:
        return datetime.now(timezone.utc).isoformat()
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(pub_date.strip(), fmt).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return datetime.now(timezone.utc).isoformat()


def fetch_from_direct_rss():
    """Fetch articles from direct source RSS feeds with real URLs and images."""
    all_articles = []

    for feed_source, feed_url in DIRECT_RSS_FEEDS:
        try:
            resp = requests.get(feed_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()

            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue

            for item in channel.findall("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                pub_date = item.findtext("pubDate", "")
                description = item.findtext("description", "")

                # Try <source> sub-element for the actual publisher name
                source_el = item.find("source")
                source_name = source_el.text if source_el is not None and source_el.text else feed_source

                # Extract image from <media:thumbnail> or <media:content>
                image_url = ""
                thumb = item.find(f"{{{_MEDIA_NS}}}thumbnail")
                if thumb is not None:
                    image_url = thumb.get("url", "")
                if not image_url:
                    content = item.find(f"{{{_MEDIA_NS}}}content")
                    if content is not None:
                        image_url = content.get("url", "")

                if not link or not title:
                    continue

                all_articles.append({
                    "title": title,
                    "source_name": source_name,
                    "url": link,
                    "published_at": _parse_rss_date(pub_date),
                    "full_text": description,
                    "description": description,
                    "image_url": image_url or None,
                })

        except requests.RequestException as e:
            logger.error(f"Direct RSS error for {feed_url}: {e}")
        except ET.ParseError as e:
            logger.error(f"Direct RSS XML parse error for {feed_url}: {e}")

    logger.info(f"Direct RSS returned {len(all_articles)} articles")
    return all_articles


def store_articles(articles):
    """Store articles in PostgreSQL, deduplicating by URL."""
    if not articles:
        return 0

    new_count = 0
    for article in articles:
        try:
            # Tag with regions and asset classes
            text = f"{article.get('title', '')} {article.get('full_text', '')}"
            regions, assets = classify_tags(text)

            result = execute_query(
                """
                INSERT INTO articles (title, source_name, url, published_at, full_text, image_url, region_tags, asset_tags, ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (url) DO UPDATE SET image_url = COALESCE(articles.image_url, EXCLUDED.image_url)
                """,
                (
                    article["title"],
                    article["source_name"],
                    article["url"],
                    article.get("published_at"),
                    article.get("full_text", ""),
                    article.get("image_url") or None,
                    regions or None,
                    assets or None,
                ),
                fetch=False,
            )
            if result and result > 0:
                new_count += 1
        except Exception as e:
            logger.error(f"Error storing article '{article.get('title', '')[:50]}': {e}")
            continue

    return new_count


def log_ingestion(articles_fetched, articles_new, status, error_message=None):
    """Log ingestion run to ingestion_logs table."""
    try:
        execute_query(
            """
            INSERT INTO ingestion_logs (articles_fetched, articles_new, themes_updated, status, error_message)
            VALUES (%s, %s, 0, %s, %s)
            """,
            (articles_fetched, articles_new, status, error_message),
            fetch=False,
        )
    except Exception as e:
        logger.error(f"Failed to log ingestion: {e}")


def run_ingestion():
    """Main ingestion orchestrator. Fetches, filters, stores, and logs."""
    logger.info("Starting news ingestion cycle...")
    all_articles = []
    errors = []

    # Fetch from all sources
    try:
        newsapi_articles = fetch_from_newsapi()
        all_articles.extend(newsapi_articles)
    except Exception as e:
        errors.append(f"NewsAPI: {e}")
        logger.error(f"NewsAPI unexpected error: {e}")

    try:
        rss_articles = fetch_from_google_rss()
        all_articles.extend(rss_articles)
    except Exception as e:
        errors.append(f"Google RSS: {e}")
        logger.error(f"Google RSS unexpected error: {e}")

    try:
        direct_articles = fetch_from_direct_rss()
        all_articles.extend(direct_articles)
    except Exception as e:
        errors.append(f"Direct RSS: {e}")
        logger.error(f"Direct RSS unexpected error: {e}")

    total_fetched = len(all_articles)
    logger.info(f"Total articles fetched: {total_fetched}")

    # Filter by financial keywords
    filtered = [a for a in all_articles if is_relevant(a)]
    logger.info(f"Articles after keyword filter: {len(filtered)} (filtered out {total_fetched - len(filtered)})")

    # Scrape OG images for articles that have none (e.g. Google RSS)
    enrich_with_og_images(filtered)

    # Store in database
    articles_new = store_articles(filtered)
    logger.info(f"New articles stored: {articles_new}")

    # Run clustering
    clustering_result = {}
    try:
        from app.services.theme_clustering import run_clustering
        clustering_result = run_clustering()
    except Exception as e:
        errors.append(f"Clustering: {e}")
        logger.error(f"Clustering error: {e}")

    # Run AI summarization on new articles
    try:
        from app.services.summarizer import summarize_unsummarized
        summarized = summarize_unsummarized(batch_size=20)
        logger.info(f"Summarized {summarized} articles")
    except Exception as e:
        errors.append(f"Summarization: {e}")
        logger.error(f"Summarization error: {e}")

    # Log the run
    status = "success" if not errors else "partial"
    error_msg = "; ".join(errors) if errors else None
    themes_updated = clustering_result.get("active_themes", 0)
    log_ingestion(total_fetched, articles_new, status, error_msg)

    return {
        "articles_fetched": total_fetched,
        "articles_filtered": len(filtered),
        "articles_new": articles_new,
        "themes_updated": themes_updated,
        "clustering": clustering_result,
        "errors": errors,
        "status": status,
    }
