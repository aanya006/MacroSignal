region_keywords = {
    "US": ["fed", "washington", "us economy"],
    "Europe": ["ecb", "european union", "germany"],
    "China": ["china", "beijing", "yuan"],
    "Global": ["global", "world"]
}

asset_keywords = {
    "Equities": ["stocks", "equities", "shares"],
    "Bonds": ["bond", "treasury", "yield"],
    "Commodities": ["oil", "gold", "gas"],
    "Crypto": ["bitcoin", "crypto", "ethereum"]
}

def classify(text):

    text = text.lower()

    region = "Unknown"
    asset = "Unknown"

    for r in region_keywords:
        if any(word in text for word in region_keywords[r]):
            region = r

    for a in asset_keywords:
        if any(word in text for word in asset_keywords[a]):
            asset = a

    return region, asset


if __name__ == "__main__":
    article = "Oil prices surged after global supply concerns."

    print(classify(article))