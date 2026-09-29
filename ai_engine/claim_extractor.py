import re


def extract_claims(response):
    """
    Break an AI-generated healthcare response into
    individual claims that can be checked separately.
    """

    if not response or not response.strip():
        return []

    # Clean unnecessary whitespace
    text = re.sub(r"\s+", " ", response.strip())

    # Split on common sentence-ending punctuation
    sentences = re.split(r"(?<=[.!?])\s+", text)

    claims = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        # Remove common bullet characters
        sentence = re.sub(r"^[•\-*]\s*", "", sentence).strip()

        # Ignore very short fragments
        if len(sentence.split()) < 4:
            continue

        claims.append(sentence)

    return claims


if __name__ == "__main__":

    test_response = """
    Vitamin C completely prevents the common cold.
    Taking 5000 mg of vitamin C every day is safe for everyone.
    Drinking enough water can help maintain normal hydration.
    """

    claims = extract_claims(test_response)

    print("\nExtracted Claims:\n")

    for number, claim in enumerate(claims, start=1):
        print(f"Claim {number}: {claim}")