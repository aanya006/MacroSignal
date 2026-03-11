"""Claude-powered article classification for Watch List themes.

Classifies articles into one of 21 curated narrative themes using Claude Sonnet,
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
        desc = defn['description']
        must_include = defn.get('must_include', '')
        must_exclude = defn.get('must_exclude', '')
        line = f"- {slug}: {defn['name']} — {desc}"
        if must_include:
            line += f"\n  MUST INCLUDE: {must_include}"
        if must_exclude:
            line += f"\n  MUST NOT INCLUDE: {must_exclude}"
        lines.append(line)
    return "\n".join(lines)


_SYSTEM_PROMPT = """You are a macro financial news classifier for institutional investors. You classify articles into exactly one of 21 curated narrative themes — or reject them as unclassifiable.

CLASSIFICATION RULES:

1. PRIMARY SUBJECT TEST: The theme must be the article's PRIMARY subject — not just mentioned, not just context. Ask: "Is this article fundamentally ABOUT this theme?" If the theme is only background context or a passing mention, return null.

2. GEOGRAPHIC PRECISION: An article mentioning a country does NOT automatically belong to that country's theme. "Singapore startup raises funding" is NOT about MAS policy. "India cricket team wins" is NOT about India growth.

3. CENTRAL BANK DISAMBIGUATION: Each central bank theme covers ONLY that specific institution:
   - "us-fed-rate-path": ONLY the US Federal Reserve (Fed, FOMC, Powell, fed funds rate)
   - "boj-yen-dynamics": ONLY the Bank of Japan (BOJ, Ueda, yield curve control, yen policy)
   - "mas-sgd-policy": ONLY the Monetary Authority of Singapore (MAS, S$NEER)
   - "china-pboc-stimulus": ONLY the People's Bank of China (PBOC, RRR, MLF, LPR)
   Articles about ECB, BOE, RBA, RBNZ, BOK, Riksbank, or other central banks → return null.
   Multi-CB roundups → classify ONLY if one of the above four is the primary focus.

4. CHINA THEME DISAMBIGUATION:
   - "china-economic-slowdown": Weak macro data, property crisis, deflation, consumer weakness — the PROBLEM
   - "china-pboc-stimulus": PBOC rate cuts, RRR cuts, fiscal packages, liquidity injections — the POLICY RESPONSE
   - "china-taiwan-indo-pacific": Military tensions, Taiwan Strait, South China Sea, AUKUS — SECURITY/GEOPOLITICAL
   If an article covers both the problem AND the response, classify under whichever is the PRIMARY focus.

5. OIL/ENERGY DISAMBIGUATION:
   - "middle-east-conflict-energy": Geopolitical conflict (Iran, Israel, Houthi, Red Sea) causing energy supply RISK
   - "opec-oil-supply": OPEC+ production decisions, quotas, Saudi-Russia coordination — supply MANAGEMENT
   If an article covers Middle East tensions AND their impact on oil, use "middle-east-conflict-energy".
   If it covers OPEC meetings/quotas with no conflict angle, use "opec-oil-supply".

6. US POLICY DISAMBIGUATION:
   - "us-policy-regime-shift": Executive orders, DOGE, deregulation, government restructuring — DOMESTIC POLICY
   - "us-china-tariffs-tech-decoupling": Bilateral tariffs, chip bans, export controls — TRADE/TECH POLICY toward China
   If an article covers Trump tariffs specifically on China → "us-china-tariffs-tech-decoupling"
   If an article covers broad deregulation or government efficiency → "us-policy-regime-shift"

7. REJECT these — return null with confidence 0.0:
   - Company earnings/product launches with no macro implications
   - Sports, entertainment, lifestyle
   - Generic market recaps ("stocks rose today") with no thematic depth
   - Press releases, promotional content
   - Articles about central banks not covered by the four themes above

CONFIDENCE CALIBRATION:
- 0.9-1.0: Article is unambiguously about this theme (e.g., "FOMC holds rates steady" → us-fed-rate-path)
- 0.75-0.89: Strong match, theme is clearly the primary subject
- 0.5-0.74: Weak or ambiguous — article touches the theme but isn't primarily about it → return null
- Below 0.5: Not relevant → return null"""


def _build_prompt():
    """Build the classification prompt with the current theme list."""
    theme_list = _build_theme_list()
    return f"""{_SYSTEM_PROMPT}

THEMES:
{theme_list}

EXAMPLES:

Article: "Federal Reserve holds rates at 5.25-5.50%, Powell signals patience on cuts"
→ {{"theme_slug": "us-fed-rate-path", "confidence": 0.95}}

Article: "ECB cuts rates by 25bps, Lagarde cites improving inflation outlook"
→ {{"theme_slug": null, "confidence": 0.0}}
(Reason: ECB has no dedicated theme)

Article: "PBOC cuts reserve requirement ratio by 50bps to support flagging economy"
→ {{"theme_slug": "china-pboc-stimulus", "confidence": 0.92}}
(Reason: PBOC policy action, not slowdown data)

Article: "China GDP growth slows to 4.7%, property investment falls 10%"
→ {{"theme_slug": "china-economic-slowdown", "confidence": 0.93}}
(Reason: macro weakness data, not policy response)

Article: "Trump signs executive order imposing 25% tariffs on Chinese semiconductors"
→ {{"theme_slug": "us-china-tariffs-tech-decoupling", "confidence": 0.94}}
(Reason: China-specific trade policy, not broad domestic policy)

Article: "Apple reports record Q4 revenue, iPhone sales beat expectations"
→ {{"theme_slug": null, "confidence": 0.0}}
(Reason: company earnings, no macro theme)

Article: "Singapore inflation eases to 2.7% as food costs moderate"
→ {{"theme_slug": null, "confidence": 0.0}}
(Reason: Singapore inflation data, but not about MAS policy decisions)

Return ONLY valid JSON: {{"theme_slug": "<slug>", "confidence": 0.0-1.0}}
If no theme fits, return: {{"theme_slug": null, "confidence": 0.0}}"""


def _get_valid_slugs():
    """Get the set of valid theme slugs from THEME_DEFINITIONS."""
    from app.services.theme_clustering import THEME_DEFINITIONS
    return set(THEME_DEFINITIONS.keys())


CONFIDENCE_THRESHOLD = 0.75


def classify_article_with_claude(title, text):
    """Classify an article into a theme slug using Claude Sonnet.

    Returns theme slug string or None. Rate-limit delay is handled by caller.
    """
    client = _get_client()
    if not client:
        return None

    prompt = _build_prompt()
    valid_slugs = _get_valid_slugs()
    # Use up to 3000 chars for better context
    user_msg = f"Title: {title}\nText: {(text or '')[:3000]}"

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[
                {"role": "user", "content": f"{prompt}\n\n{user_msg}"}
            ],
        )
        if not response.content:
            return None
        raw = response.content[0].text.strip()

        # Extract JSON object from response — Claude may wrap in code fences or add extra text
        import re
        json_match = re.search(r'\{[^}]*\}', raw)
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
            logger.info(f"Classified '{title[:60]}' → {slug} (confidence={confidence})")
            return slug
        if slug:
            logger.info(f"Rejected '{title[:60]}' → {slug} (confidence={confidence} < {CONFIDENCE_THRESHOLD})")
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
