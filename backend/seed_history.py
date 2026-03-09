"""Seed historical themes and articles for institutional memory (Story 4.1).

13 historical macro events spanning 1997–2022 with causal chains and
real article headlines. These serve as the institutional memory layer,
enabling the HistoricalParallel component to draw parallels to current
live themes.

Run once: python seed_history.py
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.db import init_db, execute_query

HISTORICAL_THEMES = [
    # ── 1. Asian Financial Crisis 1997 ──────────────────────────────
    {
        "name": "Asian Financial Crisis 1997",
        "slug": "asian-financial-crisis-1997",
        "description": "Thailand's baht devaluation triggered contagion across ASEAN, collapsing currencies, stock markets, and banking systems from Bangkok to Seoul to Jakarta.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "Thailand abandoned the baht's dollar peg on 2 July 1997 after depleting foreign reserves defending the currency against speculative attacks.",
            "mechanism": "Contagion spread as foreign investors pulled capital from all ASEAN economies. Currency collapses exposed massive unhedged dollar-denominated corporate debt, triggering bank failures and IMF bailouts across the region.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "SET (Thailand) fell 75%, JSX (Indonesia) fell 65%, STI dropped 60% from peak to trough.", "change": "-60%"},
                "bonds": {"direction": "negative", "summary": "Sovereign spreads blew out 500-1000bps across ASEAN as default risk surged.", "change": "-15%"},
                "fx": {"direction": "negative", "summary": "THB lost 50%, IDR lost 80%, MYR lost 45%, SGD weakened 20% against USD.", "change": "-45%"},
                "commodities": {"direction": "negative", "summary": "Oil fell to $10/bbl as Asian demand collapsed. Metals and rubber cratered.", "change": "-35%"},
            },
        },
        "articles": [
            {"title": "Thailand Floats Baht After Depleting Reserves, Currency Plunges 20%", "source_name": "Reuters", "url": "https://historical-seed/asian-crisis-1997/1", "published_at": "1997-07-02 08:00:00", "ai_summary": "Thailand abandons the baht's fixed exchange rate, triggering immediate 20% devaluation and fears of regional contagion."},
            {"title": "IMF Approves $17.2 Billion Bailout Package for Thailand", "source_name": "Bloomberg", "url": "https://historical-seed/asian-crisis-1997/2", "published_at": "1997-08-20 12:00:00", "ai_summary": "IMF agrees to largest-ever Asian rescue package as Thailand's financial system teeters on collapse."},
            {"title": "Indonesia Rupiah Crashes 80%, Suharto Seeks IMF Aid", "source_name": "Reuters", "url": "https://historical-seed/asian-crisis-1997/3", "published_at": "1998-01-08 09:00:00", "ai_summary": "Indonesian rupiah hits 10,000 per dollar from 2,400 pre-crisis as banking system implodes and social unrest escalates."},
            {"title": "MAS Allows Controlled SGD Depreciation as Regional Contagion Spreads", "source_name": "Straits Times", "url": "https://historical-seed/asian-crisis-1997/4", "published_at": "1998-01-12 07:00:00", "ai_summary": "Singapore dollar weakens to 1.75/USD as MAS prioritizes export competitiveness amid worst regional downturn since independence."},
        ],
    },
    # ── 2. Dot-Com Bubble Burst 2000 ───────────────────────────────
    {
        "name": "Dot-Com Bubble Burst 2000",
        "slug": "dot-com-bubble-2000",
        "description": "The NASDAQ collapsed 78% from its March 2000 peak as internet stock valuations imploded, wiping out $5 trillion in market value over two years.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "NASDAQ peaked at 5,048 on 10 March 2000 after years of speculative excess in internet stocks. The selloff began as earnings failed to materialize and the Fed tightened.",
            "mechanism": "Venture capital dried up, cash-burning dot-coms ran out of funding, and institutional investors rotated out of tech. Accounting scandals (Enron, WorldCom) deepened the crisis of confidence.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "NASDAQ fell 78% peak-to-trough. S&P 500 lost 49%. Tech giants like Cisco fell 86%.", "change": "-78%"},
                "bonds": {"direction": "positive", "summary": "Flight to quality drove 10Y Treasury yields from 6.5% to 3.5% as Fed cut rates aggressively.", "change": "+25%"},
                "fx": {"direction": "negative", "summary": "Dollar initially strengthened on safe-haven flows, then weakened as Fed slashed rates to 1%.", "change": "-5%"},
                "commodities": {"direction": "negative", "summary": "Oil fell from $35 to $20 as global growth slowed post-bubble.", "change": "-40%"},
            },
        },
        "articles": [
            {"title": "NASDAQ Hits Record 5,048 as Tech Mania Peaks", "source_name": "Bloomberg", "url": "https://historical-seed/dotcom-2000/1", "published_at": "2000-03-10 16:00:00", "ai_summary": "NASDAQ Composite reaches all-time high driven by soaring valuations of internet companies with little or no revenue."},
            {"title": "Dot-Com Darlings Pets.com and Webvan Shut Down as Funding Dries Up", "source_name": "Reuters", "url": "https://historical-seed/dotcom-2000/2", "published_at": "2000-11-07 14:00:00", "ai_summary": "High-profile internet startups collapse as venture capital evaporates and investor sentiment turns sharply against unprofitable tech firms."},
            {"title": "Fed Cuts Rates for Sixth Time in 2001 as Tech Bust Deepens Recession", "source_name": "Reuters", "url": "https://historical-seed/dotcom-2000/3", "published_at": "2001-06-27 14:30:00", "ai_summary": "Federal Reserve slashes federal funds rate to 3.75%, its sixth cut of 2001, as dot-com collapse spreads to the broader economy."},
        ],
    },
    # ── 3. Global Financial Crisis 2008 ────────────────────────────
    {
        "name": "Global Financial Crisis 2008",
        "slug": "global-financial-crisis-2008",
        "description": "Collapse of the US subprime mortgage market triggered a global banking crisis, the worst recession since the 1930s, and unprecedented central bank intervention.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "Lehman Brothers filed for bankruptcy on 15 September 2008 after losses on subprime mortgage-backed securities. AIG required $85B government bailout the next day.",
            "mechanism": "Interbank lending froze as counterparty trust evaporated. Credit markets seized up globally, forcing central banks to slash rates to zero and launch quantitative easing. Governments enacted massive fiscal stimulus.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "S&P 500 fell 57% from Oct 2007 peak. Global equity markets lost $30 trillion in value.", "change": "-57%"},
                "bonds": {"direction": "positive", "summary": "US 10Y yields crashed from 4% to 2% as flight to safety overwhelmed all other flows.", "change": "+30%"},
                "fx": {"direction": "positive", "summary": "USD surged on safe-haven demand despite being the crisis epicenter. EM currencies sold off sharply.", "change": "+15%"},
                "commodities": {"direction": "negative", "summary": "Oil crashed from $147 to $32 in six months. Copper fell 65%. Gold was the only commodity to hold.", "change": "-70%"},
            },
        },
        "articles": [
            {"title": "Lehman Brothers Files for Bankruptcy, Largest in US History", "source_name": "Reuters", "url": "https://historical-seed/gfc-2008/1", "published_at": "2008-09-15 08:00:00", "ai_summary": "Lehman Brothers Holdings files for Chapter 11 with $639 billion in assets, triggering panic across global financial markets."},
            {"title": "Fed Slashes Rates to Near Zero, Launches Quantitative Easing", "source_name": "Bloomberg", "url": "https://historical-seed/gfc-2008/2", "published_at": "2008-12-16 14:30:00", "ai_summary": "Federal Reserve cuts federal funds rate to 0-0.25% and announces plans to purchase mortgage-backed securities in unprecedented intervention."},
            {"title": "S&P 500 Hits 12-Year Low at 676 as Banking System Teeters", "source_name": "Reuters", "url": "https://historical-seed/gfc-2008/3", "published_at": "2009-03-09 16:00:00", "ai_summary": "US stocks plunge to levels not seen since 1996 amid fears of complete financial system collapse before eventual recovery begins."},
            {"title": "Singapore GDP Contracts 10% in Q1 as Trade Collapses", "source_name": "Straits Times", "url": "https://historical-seed/gfc-2008/4", "published_at": "2009-04-14 09:00:00", "ai_summary": "Singapore economy shrinks at annualized 10% rate as global trade freeze hammers the export-dependent city-state."},
        ],
    },
    # ── 4. European Debt Crisis 2011 ───────────────────────────────
    {
        "name": "European Sovereign Debt Crisis 2011",
        "slug": "european-debt-crisis-2011",
        "description": "Greece, Ireland, Portugal, and Spain faced sovereign debt crises that threatened eurozone breakup, resolved only by ECB's 'whatever it takes' intervention.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "Greece revealed its deficit was 12.7% of GDP (not 3.7% as reported), triggering loss of market access and requiring EU/IMF bailout in May 2010. Contagion spread to peripheral Europe through 2011-2012.",
            "mechanism": "Sovereign bond spreads spiked as investors feared euro breakup. Bank-sovereign doom loop amplified stress — banks held government bonds that were losing value, while governments couldn't afford to bail out banks.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "Euro Stoxx 50 fell 35%. Greek stock market lost 90% of value from 2007 peak.", "change": "-35%"},
                "bonds": {"direction": "negative", "summary": "Greek 10Y yields hit 40%. Italian and Spanish spreads over Bunds widened to 500bps+.", "change": "-20%"},
                "fx": {"direction": "negative", "summary": "EUR/USD fell from 1.49 to 1.20 on breakup fears before Draghi's intervention stabilized it.", "change": "-18%"},
                "commodities": {"direction": "negative", "summary": "Demand fears pushed oil down 25%. Gold surged to $1,900 as safe haven.", "change": "-10%"},
            },
        },
        "articles": [
            {"title": "Greece Requests EU-IMF Bailout as Bond Yields Soar Past 10%", "source_name": "Reuters", "url": "https://historical-seed/eu-debt-2011/1", "published_at": "2010-04-23 12:00:00", "ai_summary": "Greece formally requests financial assistance from eurozone partners and IMF as borrowing costs surge to unsustainable levels."},
            {"title": "Italian 10-Year Bond Yields Breach 7%, Berlusconi Resigns", "source_name": "Bloomberg", "url": "https://historical-seed/eu-debt-2011/2", "published_at": "2011-11-09 15:00:00", "ai_summary": "Italian borrowing costs cross the threshold that triggered bailouts in Greece, Ireland, and Portugal, forcing PM Berlusconi's resignation."},
            {"title": "Draghi: ECB Will Do 'Whatever It Takes' to Preserve the Euro", "source_name": "Reuters", "url": "https://historical-seed/eu-debt-2011/3", "published_at": "2012-07-26 14:00:00", "ai_summary": "ECB President Mario Draghi's three words instantly compress peripheral bond spreads and mark the turning point of the eurozone crisis."},
        ],
    },
    # ── 5. Taper Tantrum 2013 ──────────────────────────────────────
    {
        "name": "Taper Tantrum 2013",
        "slug": "taper-tantrum-2013",
        "description": "Fed Chair Bernanke's hint that QE bond purchases would slow triggered a violent selloff in emerging market assets and global bonds.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "On 22 May 2013, Bernanke told Congress the Fed could begin tapering asset purchases 'in the next few meetings' if the economy continued to improve.",
            "mechanism": "US Treasury yields surged 130bps in three months. Capital fled emerging markets as the carry trade unwound. EM currencies, bonds, and equities sold off sharply as dollar funding tightened.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "MSCI EM index fell 16%. India's Sensex dropped 12%. Indonesia and Brazil equity markets hit hardest.", "change": "-16%"},
                "bonds": {"direction": "negative", "summary": "US 10Y yield surged from 1.6% to 3.0%. EM local currency bond funds saw $25B in outflows.", "change": "-12%"},
                "fx": {"direction": "negative", "summary": "INR fell 20%, IDR fell 15%, BRL fell 18% against USD. 'Fragile Five' currencies hammered.", "change": "-18%"},
                "commodities": {"direction": "negative", "summary": "Gold crashed 25% from $1,600 to $1,200 as real rates surged. Oil held relatively steady.", "change": "-25%"},
            },
        },
        "articles": [
            {"title": "Bernanke Signals Fed Could Taper Bond Purchases, Markets Reel", "source_name": "Reuters", "url": "https://historical-seed/taper-tantrum-2013/1", "published_at": "2013-05-22 15:00:00", "ai_summary": "Fed Chairman hints at reducing QE pace, triggering sharp selloff in bonds and emerging markets globally."},
            {"title": "Emerging Market Currencies in Freefall as Capital Flees to US", "source_name": "Bloomberg", "url": "https://historical-seed/taper-tantrum-2013/2", "published_at": "2013-06-20 10:00:00", "ai_summary": "Indian rupee, Indonesian rupiah, and Brazilian real plunge as investors pull billions from EM funds on taper fears."},
            {"title": "India Raises Emergency Rates to Defend Rupee After 20% Plunge", "source_name": "Reuters", "url": "https://historical-seed/taper-tantrum-2013/3", "published_at": "2013-08-14 08:00:00", "ai_summary": "Reserve Bank of India hikes short-term rates and imposes capital controls as rupee hits record low against dollar."},
            {"title": "SGD Holds Firm as MAS S$NEER Policy Shields Singapore from Taper Fallout", "source_name": "Business Times", "url": "https://historical-seed/taper-tantrum-2013/4", "published_at": "2013-08-28 09:00:00", "ai_summary": "Singapore dollar outperforms ASEAN peers as MAS exchange rate framework and strong reserves buffer against EM contagion."},
        ],
    },
    # ── 6. Singapore Property Cooling Measures 2013 ────────────────
    {
        "name": "Singapore Property Cooling Measures 2013",
        "slug": "singapore-property-cooling-2013",
        "description": "Singapore implemented its most aggressive property cooling measures including record ABSD rates, TDSR framework, and tighter LTV limits to deflate a multi-year housing bubble.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "Private property prices rose 60% from 2009 trough. Government introduced Total Debt Servicing Ratio (TDSR) framework in June 2013 and raised Additional Buyer's Stamp Duty to 15% for foreigners.",
            "mechanism": "TDSR capped total debt obligations at 60% of income, immediately disqualifying over-leveraged buyers. Higher ABSD killed foreign speculative demand. Transaction volumes collapsed 50% within months.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "Singapore property developer stocks fell 15-25%. CapitaLand and City Developments led losses.", "change": "-20%"},
                "bonds": {"direction": "neutral", "summary": "SGS bonds unaffected. Corporate bonds of property developers saw modest spread widening.", "change": "-2%"},
                "fx": {"direction": "neutral", "summary": "SGD unaffected — cooling measures were sector-specific, not macro policy.", "change": "+0.5%"},
                "commodities": {"direction": "neutral", "summary": "No meaningful impact on commodity markets.", "change": "0%"},
            },
        },
        "articles": [
            {"title": "MAS Introduces TDSR Framework, Toughest Property Curb Yet", "source_name": "Straits Times", "url": "https://historical-seed/sg-property-2013/1", "published_at": "2013-06-29 08:00:00", "ai_summary": "MAS caps total debt servicing at 60% of gross income, closing loopholes that allowed over-leveraged property purchases."},
            {"title": "Singapore Private Home Prices Drop for First Time in 4 Years", "source_name": "Business Times", "url": "https://historical-seed/sg-property-2013/2", "published_at": "2014-01-02 09:00:00", "ai_summary": "Flash estimates show private residential prices fell 0.9% in Q4 2013, first decline since the financial crisis."},
            {"title": "Singapore Property Transaction Volume Halves After Cooling Measures", "source_name": "CNA", "url": "https://historical-seed/sg-property-2013/3", "published_at": "2013-10-15 10:00:00", "ai_summary": "Developer sales plunge 49% year-on-year as TDSR and higher ABSD rates freeze speculative activity."},
        ],
    },
    # ── 7. China A-Share Bubble & Bust 2015 ────────────────────────
    {
        "name": "China A-Share Bubble & Bust 2015",
        "slug": "china-a-share-crash-2015",
        "description": "China's stock market surged 150% in 12 months fueled by margin lending, then crashed 45% in weeks. PBOC intervened with rate cuts, trading halts, and a surprise yuan devaluation.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "Shanghai Composite peaked at 5,178 on 12 June 2015 after a margin-lending fueled rally. Regulators tightened margin rules, triggering cascading forced liquidations.",
            "mechanism": "Retail margin accounts unwound simultaneously. Circuit breakers amplified panic by trapping sellers. PBOC cut rates and RRR, suspended IPOs, and deployed state funds to buy equities. Then devalued the yuan on 11 Aug, shocking global markets.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "Shanghai Composite fell 45% in 2 months. $5 trillion in market value erased. Global equities sold off in sympathy.", "change": "-45%"},
                "bonds": {"direction": "positive", "summary": "Chinese government bond yields fell 50bps as PBOC cut rates. Safe-haven bid in Treasuries.", "change": "+5%"},
                "fx": {"direction": "negative", "summary": "PBOC devalued yuan 3% on 11 Aug, triggering EM FX contagion. SGD weakened 4% in sympathy.", "change": "-6%"},
                "commodities": {"direction": "negative", "summary": "Iron ore fell 20%, copper fell 15% on China demand fears. Oil dropped below $40.", "change": "-20%"},
            },
        },
        "articles": [
            {"title": "Shanghai Composite Hits 5,178 as Margin Lending Frenzy Peaks", "source_name": "Bloomberg", "url": "https://historical-seed/china-crash-2015/1", "published_at": "2015-06-12 09:00:00", "ai_summary": "Chinese stocks reach 7-year high as retail investors open record margin accounts, many borrowing against homes to speculate."},
            {"title": "China Markets in Freefall: $3 Trillion Wiped Out in Three Weeks", "source_name": "Reuters", "url": "https://historical-seed/china-crash-2015/2", "published_at": "2015-07-08 10:00:00", "ai_summary": "Shanghai index crashes 30% as margin calls cascade and circuit breakers trap panicked sellers. Over 1,000 stocks hit daily limit down."},
            {"title": "PBOC Shocks Markets with Surprise 3% Yuan Devaluation", "source_name": "Reuters", "url": "https://historical-seed/china-crash-2015/3", "published_at": "2015-08-11 09:30:00", "ai_summary": "People's Bank of China devalues yuan fixing by 1.9%, largest single-day move ever, sparking fears of competitive devaluation across Asia."},
            {"title": "Black Monday: Global Stocks Plunge as China Fears Grip Markets", "source_name": "Bloomberg", "url": "https://historical-seed/china-crash-2015/4", "published_at": "2015-08-24 16:00:00", "ai_summary": "Dow Jones falls 1,000 points at open, S&P 500 enters correction as China slowdown fears and yuan devaluation trigger global panic."},
        ],
    },
    # ── 8. Swiss Franc Peg Removal 2015 ────────────────────────────
    {
        "name": "Swiss Franc Peg Removal 2015",
        "slug": "snb-peg-removal-2015",
        "description": "Swiss National Bank abruptly removed the EUR/CHF 1.20 floor on 15 January 2015, causing the franc to surge 30% in minutes and bankrupting multiple FX brokers.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "SNB abandoned the EUR/CHF 1.20 minimum exchange rate without warning, reversing a policy maintained since September 2011, ahead of anticipated ECB quantitative easing.",
            "mechanism": "CHF surged 30% against EUR in minutes as stop-losses cascaded. Leveraged FX positions were wiped out. Multiple retail FX brokers went bankrupt. Central bank credibility globally was questioned.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "Swiss Market Index fell 10% on the day. European equities dropped 2-3% on contagion fears.", "change": "-10%"},
                "bonds": {"direction": "positive", "summary": "Swiss government bond yields went deeply negative. Flight to safety boosted core European bonds.", "change": "+8%"},
                "fx": {"direction": "positive", "summary": "EUR/CHF crashed from 1.20 to 0.85 intraday before settling near 1.00. Largest G10 FX move in modern history.", "change": "+30%"},
                "commodities": {"direction": "neutral", "summary": "Gold rose 2% on safe-haven demand. Limited broader commodity impact.", "change": "+2%"},
            },
        },
        "articles": [
            {"title": "SNB Shocks Markets, Removes Swiss Franc Cap Against Euro", "source_name": "Reuters", "url": "https://historical-seed/snb-peg-2015/1", "published_at": "2015-01-15 10:30:00", "ai_summary": "Swiss National Bank stuns markets by abandoning the 1.20 EUR/CHF floor, sending the franc surging 30% and triggering chaos across FX markets."},
            {"title": "FX Broker FXCM Needs $300M Bailout After Swiss Franc Shock", "source_name": "Bloomberg", "url": "https://historical-seed/snb-peg-2015/2", "published_at": "2015-01-16 14:00:00", "ai_summary": "Largest US retail FX broker faces insolvency as client losses from Swiss franc surge exceed firm's equity."},
            {"title": "Central Bank Credibility Under Scrutiny After SNB U-Turn", "source_name": "FT", "url": "https://historical-seed/snb-peg-2015/3", "published_at": "2015-01-19 08:00:00", "ai_summary": "Markets question whether central banks can be trusted after SNB abandoned a policy it insisted was non-negotiable just weeks earlier."},
        ],
    },
    # ── 9. Trump Trade War 1.0 (2018) ──────────────────────────────
    {
        "name": "US-China Trade War 2018",
        "slug": "us-china-trade-war-2018",
        "description": "Trump imposed escalating tariffs on $360 billion of Chinese goods starting March 2018, triggering retaliatory tariffs and supply chain disruption across Asia.",
        "score_label": "cool",
        "score_value": 2.0,
        "causal_chain": {
            "trigger": "Trump signed tariffs on $50B of Chinese goods in March 2018, escalating to $200B by September with threatened 25% rates, citing unfair trade practices and IP theft.",
            "mechanism": "Tariff uncertainty froze corporate capex and disrupted supply chains. Companies accelerated China+1 strategies. Retaliatory Chinese tariffs hit US agriculture. Trade-dependent Asian economies suffered collateral damage.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "S&P 500 fell 20% in Q4 2018. Shanghai Composite dropped 25% for the year. ASEAN markets fell 10-15%.", "change": "-20%"},
                "bonds": {"direction": "positive", "summary": "US 10Y yield fell from 3.2% to 2.6% as growth fears mounted and Fed pivoted to cuts.", "change": "+8%"},
                "fx": {"direction": "negative", "summary": "CNY weakened from 6.3 to 6.97/USD. Asian FX broadly weaker on trade uncertainty.", "change": "-10%"},
                "commodities": {"direction": "negative", "summary": "Soybeans fell 20% on Chinese retaliatory tariffs. Copper dropped 15% on global growth fears.", "change": "-15%"},
            },
        },
        "articles": [
            {"title": "Trump Signs Tariffs on $50B of Chinese Goods, Beijing Retaliates", "source_name": "Reuters", "url": "https://historical-seed/trade-war-2018/1", "published_at": "2018-03-22 16:00:00", "ai_summary": "President Trump imposes 25% tariffs on Chinese imports citing intellectual property theft, China immediately announces retaliatory tariffs on US goods."},
            {"title": "US Escalates to $200B in China Tariffs, Markets Slide", "source_name": "Bloomberg", "url": "https://historical-seed/trade-war-2018/2", "published_at": "2018-09-17 14:00:00", "ai_summary": "Trump expands tariffs to cover $200 billion of Chinese goods at 10% rate, threatening increase to 25% if no deal reached."},
            {"title": "Singapore GDP Growth Slows as US-China Trade War Hits Exports", "source_name": "CNA", "url": "https://historical-seed/trade-war-2018/3", "published_at": "2018-11-22 09:00:00", "ai_summary": "Singapore's export-dependent economy feels trade war impact as NODX falls for third straight month amid global supply chain disruption."},
            {"title": "Fed Pivots to Rate Cuts as Trade War Uncertainty Weighs on Economy", "source_name": "Reuters", "url": "https://historical-seed/trade-war-2018/4", "published_at": "2019-07-31 14:30:00", "ai_summary": "Federal Reserve cuts rates for first time since 2008, citing trade uncertainty and global slowdown as key risks to US economic outlook."},
        ],
    },
    # ── 10. Turkey/Argentina EM Currency Crisis 2018 ───────────────
    {
        "name": "Turkey-Argentina EM Currency Crisis 2018",
        "slug": "em-currency-crisis-2018",
        "description": "Turkish lira and Argentine peso collapsed in 2018 as rising US rates, current account deficits, and political mismanagement triggered capital flight from vulnerable emerging markets.",
        "score_label": "cool",
        "score_value": 1.5,
        "causal_chain": {
            "trigger": "Turkey's lira crashed 40% in August 2018 after Erdogan refused to raise rates despite 25% inflation, combined with a diplomatic spat with the US. Argentina's peso fell 50% as IMF bailout failed to restore confidence.",
            "mechanism": "Rising US rates and strong dollar exposed EM countries with large external deficits and dollar-denominated debt. Contagion spread to South Africa (ZAR -25%), India (INR -13%), and Indonesia (IDR -10%).",
            "impacts": {
                "equities": {"direction": "negative", "summary": "MSCI EM fell 17% from Jan peak. Turkey's BIST dropped 40% in dollar terms.", "change": "-17%"},
                "bonds": {"direction": "negative", "summary": "EM hard currency bond spreads widened 100bps. Turkey and Argentina sovereign CDS surged to distressed levels.", "change": "-10%"},
                "fx": {"direction": "negative", "summary": "TRY lost 40%, ARS lost 50%, ZAR lost 25%. Fragile Five narrative returned.", "change": "-30%"},
                "commodities": {"direction": "negative", "summary": "Broad risk-off sentiment pushed oil down 10%. Gold fell as dollar strengthened.", "change": "-8%"},
            },
        },
        "articles": [
            {"title": "Turkish Lira Crashes 20% in Single Day as Erdogan Defies Markets", "source_name": "Reuters", "url": "https://historical-seed/em-crisis-2018/1", "published_at": "2018-08-10 12:00:00", "ai_summary": "Lira plunges to record low as President Erdogan refuses to raise interest rates and US doubles steel tariffs on Turkey."},
            {"title": "Argentina Requests $50B IMF Bailout as Peso Collapses", "source_name": "Bloomberg", "url": "https://historical-seed/em-crisis-2018/2", "published_at": "2018-05-08 15:00:00", "ai_summary": "Argentina turns to IMF for largest-ever bailout as peso falls 50% and inflation spirals above 40%."},
            {"title": "EM Contagion Spreads: Rupee, Rupiah, Rand All Under Pressure", "source_name": "Reuters", "url": "https://historical-seed/em-crisis-2018/3", "published_at": "2018-09-05 08:00:00", "ai_summary": "Emerging market currencies from India to Indonesia to South Africa weaken sharply as Turkey-Argentina crisis triggers broad capital flight."},
        ],
    },
    # ── 11. Saudi-Russia Oil Price War 2020 ────────────────────────
    {
        "name": "Saudi-Russia Oil Price War 2020",
        "slug": "oil-price-war-2020",
        "description": "OPEC+ alliance collapsed in March 2020 as Saudi Arabia and Russia launched a price war, flooding markets with crude just as COVID-19 destroyed global oil demand.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "Russia refused OPEC+ production cuts on 6 March 2020. Saudi Arabia retaliated by slashing official selling prices and pledging to flood the market with 12.3 million bpd.",
            "mechanism": "Supply surge collided with COVID-19 demand destruction. Storage filled globally. WTI futures briefly went negative (-$37/bbl) for the first time in history. Energy companies slashed capex and cut dividends.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "S&P Energy sector fell 50%. Saudi Aramco dropped below IPO price. Oil majors cut dividends for first time in decades.", "change": "-50%"},
                "bonds": {"direction": "negative", "summary": "US high yield energy spreads blew out to 1,100bps. Wave of energy defaults followed.", "change": "-25%"},
                "fx": {"direction": "negative", "summary": "Oil-linked currencies (NOK, CAD, RUB, MYR) weakened 10-20% against USD.", "change": "-15%"},
                "commodities": {"direction": "negative", "summary": "Brent fell from $65 to $20. WTI went negative at -$37.63. Natural gas and NGL prices collapsed.", "change": "-70%"},
            },
        },
        "articles": [
            {"title": "OPEC+ Talks Collapse as Russia Refuses Production Cuts", "source_name": "Reuters", "url": "https://historical-seed/oil-war-2020/1", "published_at": "2020-03-06 16:00:00", "ai_summary": "Russia walks away from OPEC+ negotiations, rejecting proposed 1.5 million bpd cut and ending three years of production cooperation."},
            {"title": "Saudi Arabia Launches Oil Price War, Slashes Prices by $8/bbl", "source_name": "Bloomberg", "url": "https://historical-seed/oil-war-2020/2", "published_at": "2020-03-08 08:00:00", "ai_summary": "Saudi Aramco cuts April official selling prices by unprecedented $6-8/bbl and pledges to boost output to 12.3 million bpd."},
            {"title": "Oil Goes Negative: WTI Crashes to -$37 as Storage Runs Out", "source_name": "Reuters", "url": "https://historical-seed/oil-war-2020/3", "published_at": "2020-04-20 14:30:00", "ai_summary": "May WTI futures settle at negative $37.63 per barrel — traders paying to offload contracts as Cushing storage nears capacity."},
        ],
    },
    # ── 12. COVID Market Crash & Recovery 2020 ─────────────────────
    {
        "name": "COVID-19 Market Crash & Recovery 2020",
        "slug": "covid-crash-2020",
        "description": "Global markets crashed 35% in the fastest bear market in history, then staged the sharpest recovery ever as central banks unleashed unlimited QE and governments deployed trillions in fiscal stimulus.",
        "score_label": "cool",
        "score_value": 1.0,
        "causal_chain": {
            "trigger": "WHO declared COVID-19 a pandemic on 11 March 2020. Countries imposed lockdowns, shutting down economic activity globally within weeks.",
            "mechanism": "Fed cut rates to zero and launched unlimited QE within days. Congress passed $2.2T CARES Act. ECB, BOJ, and others followed. Unprecedented liquidity flooded markets, driving the fastest recovery from bear market in history.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "S&P 500 fell 34% in 23 trading days — fastest bear market ever. Then rallied 68% to new highs by year-end.", "change": "-34%"},
                "bonds": {"direction": "positive", "summary": "US 10Y yield fell from 1.9% to 0.5%. Fed bought $2T+ in Treasuries and MBS.", "change": "+20%"},
                "fx": {"direction": "positive", "summary": "USD spiked on initial panic (DXY +8%), then weakened sharply as Fed flooded dollar liquidity globally.", "change": "-7%"},
                "commodities": {"direction": "negative", "summary": "Oil crashed 65%. Gold initially fell, then surged to record $2,075 on unlimited money printing.", "change": "+25%"},
            },
        },
        "articles": [
            {"title": "WHO Declares COVID-19 a Pandemic as Cases Surge Globally", "source_name": "Reuters", "url": "https://historical-seed/covid-2020/1", "published_at": "2020-03-11 18:00:00", "ai_summary": "World Health Organization officially characterizes COVID-19 as a pandemic, with 118,000 cases across 114 countries."},
            {"title": "S&P 500 Crashes 12% in Worst Day Since 1987 Black Monday", "source_name": "Bloomberg", "url": "https://historical-seed/covid-2020/2", "published_at": "2020-03-16 16:00:00", "ai_summary": "US stocks suffer worst single-day drop in 33 years as lockdown fears grip markets. Circuit breakers triggered for third time in a week."},
            {"title": "Fed Goes All-In: Unlimited QE, Corporate Bond Purchases Announced", "source_name": "Reuters", "url": "https://historical-seed/covid-2020/3", "published_at": "2020-03-23 08:00:00", "ai_summary": "Federal Reserve removes all limits on Treasury and MBS purchases and announces unprecedented corporate bond buying program."},
            {"title": "Singapore Circuit Breaker: PM Lee Announces Nationwide Lockdown", "source_name": "CNA", "url": "https://historical-seed/covid-2020/4", "published_at": "2020-04-03 20:00:00", "ai_summary": "Singapore implements strictest COVID-19 measures: all non-essential workplaces closed, schools move to home-based learning."},
        ],
    },
    # ── 13. Russia-Ukraine Commodity Shock 2022 ────────────────────
    {
        "name": "Russia-Ukraine Commodity Shock 2022",
        "slug": "russia-ukraine-shock-2022",
        "description": "Russia's invasion of Ukraine in February 2022 caused the largest commodity supply shock since the 1970s, spiking energy and grain prices and accelerating the global inflation crisis.",
        "score_label": "cool",
        "score_value": 2.0,
        "causal_chain": {
            "trigger": "Russia invaded Ukraine on 24 February 2022. Western nations imposed sweeping sanctions including freezing Russia's central bank reserves and cutting major banks from SWIFT.",
            "mechanism": "Russia supplies 10% of global oil, 17% of gas, 20% of wheat. Sanctions and supply disruption spiked commodity prices, worsened the post-COVID inflation surge, and forced central banks into aggressive tightening.",
            "impacts": {
                "equities": {"direction": "negative", "summary": "European stocks fell 15%. Russian MOEX collapsed 50% and was closed for a month. Global equities entered bear market.", "change": "-15%"},
                "bonds": {"direction": "negative", "summary": "Global bonds had worst year in centuries. US 10Y yield surged from 1.5% to 4.2% as inflation hit 9%.", "change": "-20%"},
                "fx": {"direction": "positive", "summary": "EUR fell below parity with USD for first time since 2002 on energy crisis fears. Ruble initially crashed 50%, then recovered on capital controls.", "change": "+15%"},
                "commodities": {"direction": "positive", "summary": "Brent hit $130/bbl. European gas surged 400%. Wheat hit record highs. Nickel doubled in 24 hours, forcing LME to halt trading.", "change": "+60%"},
            },
        },
        "articles": [
            {"title": "Russia Invades Ukraine: Full-Scale Military Offensive Launched", "source_name": "Reuters", "url": "https://historical-seed/ukraine-2022/1", "published_at": "2022-02-24 05:00:00", "ai_summary": "Russian forces launch missiles and ground offensive across Ukraine, triggering the largest military conflict in Europe since World War II."},
            {"title": "Brent Surges Past $130 as Western Sanctions Target Russian Oil", "source_name": "Bloomberg", "url": "https://historical-seed/ukraine-2022/2", "published_at": "2022-03-07 10:00:00", "ai_summary": "Oil prices spike to highest since 2008 as US and allies consider banning Russian crude imports and shipping disruptions mount."},
            {"title": "LME Halts Nickel Trading After Unprecedented 250% Surge", "source_name": "Reuters", "url": "https://historical-seed/ukraine-2022/3", "published_at": "2022-03-08 14:00:00", "ai_summary": "London Metal Exchange suspends nickel trading and cancels trades after prices doubled in hours due to massive short squeeze on Russia supply fears."},
            {"title": "Global Wheat Prices Hit Record as Ukraine Ports Blockaded", "source_name": "Reuters", "url": "https://historical-seed/ukraine-2022/4", "published_at": "2022-03-14 08:00:00", "ai_summary": "Wheat futures surge to all-time high as Russia's Black Sea blockade cuts off Ukraine, which supplies 10% of global wheat exports."},
        ],
    },
]


def seed():
    init_db()

    # Clear old historical seeds (keep live themes intact)
    old_slugs = [
        "fed-rate-pivot-2024", "mas-oct-2024-policy", "china-property-crisis-2024",
        "japan-ycc-end-2024", "us-china-tech-decoupling-2024",
    ]
    for slug in old_slugs:
        rows = execute_query("SELECT id FROM themes WHERE slug = %s", (slug,))
        if rows:
            theme_id = rows[0]["id"]
            execute_query("DELETE FROM articles WHERE theme_id = %s", (theme_id,), fetch=False)
            execute_query("DELETE FROM theme_history WHERE theme_id = %s", (theme_id,), fetch=False)
            execute_query("DELETE FROM themes WHERE id = %s", (theme_id,), fetch=False)
            print(f"  Removed old seed: {slug}")

    seeded_themes = 0
    seeded_articles = 0

    for ht in HISTORICAL_THEMES:
        # Insert theme
        try:
            execute_query(
                """
                INSERT INTO themes (name, slug, description, score_label, score_value, article_count, first_seen_at, last_updated_at, causal_chain, is_historical)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    causal_chain = EXCLUDED.causal_chain,
                    score_label = EXCLUDED.score_label,
                    score_value = EXCLUDED.score_value,
                    article_count = EXCLUDED.article_count,
                    first_seen_at = EXCLUDED.first_seen_at,
                    last_updated_at = EXCLUDED.last_updated_at,
                    is_historical = TRUE
                """,
                (
                    ht["name"], ht["slug"], ht["description"],
                    ht["score_label"], ht["score_value"], len(ht["articles"]),
                    ht["articles"][0]["published_at"],
                    ht["articles"][-1]["published_at"],
                    json.dumps(ht.get("causal_chain")) if ht.get("causal_chain") else None,
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
