from openai import OpenAI

client = OpenAI()

def summarize(text):

    prompt = f"Summarize this macroeconomic news in 3 sentences:\n\n{text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    article = """
    The Federal Reserve raised interest rates again in an effort to fight
    persistent inflation pressures across the US economy.
    """

    print(summarize(article))