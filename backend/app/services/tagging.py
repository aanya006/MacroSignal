"""Region and asset class tagging for articles (Story 2.1).

Based on Person 3's ai/region_asset_classifier.py, expanded with full
keyword maps and multi-tag support per the AC requirements.
"""
import re

# Regions required by AC: Singapore, US, China, ASEAN, EU, Japan
REGION_KEYWORDS = {
    "Singapore": [
        "singapore", "sgd", "neer", "s\\$neer", "straits times",
        "temasek", "\\bmas\\b", "\\bgic\\b", "\\bdbs\\b", "ocbc", "\\buob\\b",
    ],
    "US": [
        "\\bu\\.?s\\.?\\b", "united states", "america", "federal reserve",
        "\\bfed\\b", "fomc", "powell", "wall street", "nasdaq", "s&p 500",
        "dow jones", "treasury", "washington",
    ],
    "China": [
        "china", "chinese", "beijing", "pboc", "yuan", "renminbi", "\\brmb\\b",
        "shanghai", "shenzhen", "hong kong", "evergrande", "huawei",
    ],
    "ASEAN": [
        "asean", "southeast asia", "indonesia", "malaysia", "thailand",
        "vietnam", "philippines", "myanmar", "cambodia", "laos",
    ],
    "EU": [
        "\\becb\\b", "european", "eurozone", "\\beu\\b", "lagarde",
        "\\beuro\\b", "germany", "france", "brussels", "bundesbank",
    ],
    "Japan": [
        "japan", "\\bboj\\b", "bank of japan", "\\byen\\b", "tokyo", "nikkei",
        "ueda", "yield curve control",
    ],
}

# Asset classes required by AC: Equities, Bonds, FX, Commodities
ASSET_KEYWORDS = {
    "Equities": [
        "equit", "stock", "shares", "nasdaq", "s&p", "dow jones", "nikkei",
        "hang seng", "\\bsti\\b", "bull market", "bear market",
        "tech sector", "semiconductor", "stock market",
    ],
    "Bonds": [
        "bond", "treasury", "\\byield\\b", "sovereign debt", "fixed income",
        "credit spread", "coupon", "maturity",
    ],
    "FX": [
        "forex", "\\bfx\\b", "currency", "exchange rate", "dollar index", "\\bdxy\\b",
        "\\bsgd\\b", "\\byuan\\b", "\\byen\\b", "\\beuro\\b", "sterling", "\\bgbp\\b",
        "\\bdollar\\b",
    ],
    "Commodities": [
        "\\boil\\b", "crude", "brent", "gold", "silver", "copper", "commodity",
        "commodities", "iron ore", "natural gas", "opec", "metals",
    ],
}

# Pre-compile all patterns for performance
_REGION_PATTERNS = {
    region: [re.compile(kw, re.IGNORECASE) for kw in keywords]
    for region, keywords in REGION_KEYWORDS.items()
}
_ASSET_PATTERNS = {
    asset: [re.compile(kw, re.IGNORECASE) for kw in keywords]
    for asset, keywords in ASSET_KEYWORDS.items()
}


def classify_tags(text):
    """Classify article text into region and asset class tags.

    Returns:
        tuple: (list of region strings, list of asset class strings)
    """
    regions = []
    for region, patterns in _REGION_PATTERNS.items():
        if any(p.search(text) for p in patterns):
            regions.append(region)

    assets = []
    for asset, patterns in _ASSET_PATTERNS.items():
        if any(p.search(text) for p in patterns):
            assets.append(asset)

    return regions, assets
