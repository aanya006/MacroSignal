"""Seed historical themes and articles for institutional memory demo (Story 4.1).

Run once: python seed_history.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.db import init_db, execute_query

HISTORICAL_THEMES = [
    {
        "name": "Fed Rate Pivot 2024",
        "slug": "fed-rate-pivot-2024",
        "description": "Federal Reserve began rate cutting cycle in September 2024 after holding rates at 5.25-5.50% for over a year.",
        "score_label": "cool",
        "score_value": 2.0,
        "articles": [
            {
                "title": "Fed Cuts Rates by 50bps in Surprise Move, First Cut Since 2020",
                "source_name": "Reuters",
                "url": "https://historical-seed/fed-rate-pivot-2024/1",
                "published_at": "2024-09-18 14:30:00",
                "ai_summary": "The Federal Reserve cut interest rates by 50 basis points to 4.75-5.00%, marking the first rate reduction since March 2020.",
            },
            {
                "title": "Markets Rally as Powell Signals More Cuts Ahead in 2024",
                "source_name": "Bloomberg",
                "url": "https://historical-seed/fed-rate-pivot-2024/2",
                "published_at": "2024-09-18 18:00:00",
                "ai_summary": "S&P 500 surges 1.7% as Chair Powell indicates additional rate cuts likely before year-end.",
            },
            {
                "title": "Asia FX Strengthens After Fed Rate Decision, SGD Hits 3-Month High",
                "source_name": "CNA",
                "url": "https://historical-seed/fed-rate-pivot-2024/3",
                "published_at": "2024-09-19 08:00:00",
                "ai_summary": "Asian currencies rally broadly with SGD reaching strongest level since June as dollar weakens on Fed pivot.",
            },
            {
                "title": "Fed Delivers Second Rate Cut, Reduces by 25bps to 4.50-4.75%",
                "source_name": "Reuters",
                "url": "https://historical-seed/fed-rate-pivot-2024/4",
                "published_at": "2024-11-07 14:30:00",
                "ai_summary": "Federal Reserve cuts rates by 25 basis points in November meeting, continuing its easing cycle.",
            },
        ],
    },
    {
        "name": "MAS Oct 2024 Policy Review",
        "slug": "mas-oct-2024-policy",
        "description": "MAS maintained its monetary policy stance in October 2024, keeping the S$NEER band unchanged amid global rate cutting cycle.",
        "score_label": "cool",
        "score_value": 1.5,
        "articles": [
            {
                "title": "MAS Keeps S$NEER Policy Band Unchanged at October Review",
                "source_name": "Business Times",
                "url": "https://historical-seed/mas-oct-2024/1",
                "published_at": "2024-10-14 09:00:00",
                "ai_summary": "MAS maintains its exchange rate-based monetary policy, keeping the slope and width of the S$NEER band unchanged.",
            },
            {
                "title": "Singapore Core Inflation Eases to 2.7% Ahead of MAS Decision",
                "source_name": "CNA",
                "url": "https://historical-seed/mas-oct-2024/2",
                "published_at": "2024-10-11 10:00:00",
                "ai_summary": "Core inflation moderates for fifth straight month, supporting MAS decision to hold policy steady.",
            },
            {
                "title": "Analysts: MAS Likely to Ease in April 2025 as Inflation Cools",
                "source_name": "Straits Times",
                "url": "https://historical-seed/mas-oct-2024/3",
                "published_at": "2024-10-15 07:30:00",
                "ai_summary": "Market consensus shifts toward MAS easing at next review as Singapore inflation continues downward trend.",
            },
        ],
    },
    {
        "name": "China Property Crisis 2024",
        "slug": "china-property-crisis-2024",
        "description": "China's prolonged property sector downturn deepened in 2024 with major developers defaulting and government stimulus failing to restore confidence.",
        "score_label": "cool",
        "score_value": 3.0,
        "articles": [
            {
                "title": "Evergrande Ordered to Liquidate by Hong Kong Court",
                "source_name": "Reuters",
                "url": "https://historical-seed/china-property-2024/1",
                "published_at": "2024-01-29 10:00:00",
                "ai_summary": "Hong Kong court orders liquidation of China Evergrande Group after failed debt restructuring, sending shockwaves through Asian markets.",
            },
            {
                "title": "China Unveils Largest Property Rescue Package, Cuts Mortgage Rates",
                "source_name": "Bloomberg",
                "url": "https://historical-seed/china-property-2024/2",
                "published_at": "2024-05-17 12:00:00",
                "ai_summary": "China announces unprecedented property support including removing mortgage rate floors and easing down payment requirements.",
            },
            {
                "title": "China Property Sales Slump 20% in 2024, Recovery Elusive Despite Stimulus",
                "source_name": "SCMP",
                "url": "https://historical-seed/china-property-2024/3",
                "published_at": "2024-08-15 09:00:00",
                "ai_summary": "New home sales by top 100 developers fall 20% year-on-year despite government rescue measures, deepening sector gloom.",
            },
            {
                "title": "Country Garden Misses Bond Payment, Defaults on Dollar Debt",
                "source_name": "Reuters",
                "url": "https://historical-seed/china-property-2024/4",
                "published_at": "2024-02-27 14:00:00",
                "ai_summary": "China's largest private developer Country Garden formally defaults on US dollar bonds after exhausting grace periods.",
            },
        ],
    },
    {
        "name": "Japan Yield Curve Control End",
        "slug": "japan-ycc-end-2024",
        "description": "Bank of Japan ended negative interest rates and yield curve control in March 2024, the first rate hike since 2007.",
        "score_label": "cool",
        "score_value": 1.0,
        "articles": [
            {
                "title": "BOJ Ends Negative Rates, Raises Interest Rate for First Time Since 2007",
                "source_name": "Reuters",
                "url": "https://historical-seed/japan-ycc-2024/1",
                "published_at": "2024-03-19 06:00:00",
                "ai_summary": "Bank of Japan raises short-term rate to 0-0.1% from -0.1%, ending the world's last negative rate regime and abandoning yield curve control.",
            },
            {
                "title": "Yen Weakens Past 150 Despite BOJ Hike, Markets Underwhelmed",
                "source_name": "Bloomberg",
                "url": "https://historical-seed/japan-ycc-2024/2",
                "published_at": "2024-03-19 12:00:00",
                "ai_summary": "Japanese yen falls to 150.7 per dollar as markets view BOJ's dovish guidance as signal that further hikes will be slow.",
            },
            {
                "title": "BOJ Governor Ueda: We Will Proceed Cautiously on Further Rate Hikes",
                "source_name": "Nikkei Asia",
                "url": "https://historical-seed/japan-ycc-2024/3",
                "published_at": "2024-03-20 08:00:00",
                "ai_summary": "Governor Ueda emphasizes accommodative conditions will persist, dampening expectations of rapid normalization.",
            },
        ],
    },
    {
        "name": "US-China Tech Decoupling 2024",
        "slug": "us-china-tech-decoupling-2024",
        "description": "US expanded semiconductor export controls against China in 2024, accelerating tech supply chain fragmentation across Asia.",
        "score_label": "cool",
        "score_value": 2.5,
        "articles": [
            {
                "title": "US Tightens AI Chip Export Controls, Targets NVIDIA H20 Sales to China",
                "source_name": "Reuters",
                "url": "https://historical-seed/us-china-tech-2024/1",
                "published_at": "2024-04-15 16:00:00",
                "ai_summary": "Biden administration expands semiconductor restrictions, limiting NVIDIA's ability to sell even downgraded AI chips to Chinese firms.",
            },
            {
                "title": "TSMC Caught in US-China Crossfire as Chip Restrictions Expand",
                "source_name": "Bloomberg",
                "url": "https://historical-seed/us-china-tech-2024/2",
                "published_at": "2024-06-20 10:00:00",
                "ai_summary": "Taiwan Semiconductor faces growing pressure from US rules limiting advanced chip manufacturing for Chinese clients.",
            },
            {
                "title": "Singapore Chip Firms Pivot Supply Chains as US-China Tech War Deepens",
                "source_name": "Business Times",
                "url": "https://historical-seed/us-china-tech-2024/3",
                "published_at": "2024-07-08 09:00:00",
                "ai_summary": "Singapore semiconductor companies diversify sourcing and customers amid intensifying US-China technology restrictions.",
            },
            {
                "title": "China's Huawei Launches Domestic AI Chip to Bypass US Sanctions",
                "source_name": "SCMP",
                "url": "https://historical-seed/us-china-tech-2024/4",
                "published_at": "2024-08-22 11:00:00",
                "ai_summary": "Huawei unveils Ascend 910C processor as China accelerates homegrown semiconductor development in response to export controls.",
            },
        ],
    },
]


def seed():
    init_db()

    seeded_themes = 0
    seeded_articles = 0

    for ht in HISTORICAL_THEMES:
        # Insert theme
        try:
            execute_query(
                """
                INSERT INTO themes (name, slug, description, score_label, score_value, article_count, first_seen_at, last_updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO NOTHING
                """,
                (
                    ht["name"], ht["slug"], ht["description"],
                    ht["score_label"], ht["score_value"], len(ht["articles"]),
                    ht["articles"][0]["published_at"],  # first_seen = earliest article
                    ht["articles"][-1]["published_at"],  # last_updated = latest article
                ),
                fetch=False,
            )
            seeded_themes += 1
        except Exception as e:
            print(f"Error seeding theme '{ht['slug']}': {e}")
            continue

        # Get theme ID
        rows = execute_query("SELECT id FROM themes WHERE slug = %s", (ht["slug"],))
        if not rows:
            continue
        theme_id = rows[0]["id"]

        # Insert articles
        for art in ht["articles"]:
            try:
                execute_query(
                    """
                    INSERT INTO articles (title, source_name, url, published_at, ai_summary, theme_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    """,
                    (art["title"], art["source_name"], art["url"], art["published_at"], art["ai_summary"], theme_id),
                    fetch=False,
                )
                seeded_articles += 1
            except Exception as e:
                print(f"Error seeding article: {e}")

        # Snapshot to theme_history
        snapshot_date = ht["articles"][-1]["published_at"][:10]
        try:
            execute_query(
                """
                INSERT INTO theme_history (theme_id, snapshot_date, score_label, score_value, article_count)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (theme_id, snapshot_date) DO NOTHING
                """,
                (theme_id, snapshot_date, ht["score_label"], ht["score_value"], len(ht["articles"])),
                fetch=False,
            )
        except Exception as e:
            print(f"Error seeding history: {e}")

    print(f"Seeded {seeded_themes} historical themes with {seeded_articles} articles")


if __name__ == "__main__":
    seed()
