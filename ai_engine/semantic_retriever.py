"""
MEDTRUST AI - Semantic Retrieval Engine

Uses a pretrained sentence-embedding model to compare the meaning
of healthcare claims with the meaning of trusted evidence.

IMPORTANT:
    Semantic similarity measures relevance, NOT medical truth.

    A high similarity score means:
        "This evidence is probably relevant to this claim."

    It does NOT mean:
        "The claim is medically correct."

The verifier and risk analyzer remain responsible for safety decisions.
"""

from functools import lru_cache

from sentence_transformers import SentenceTransformer, util


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    """
    Load the pretrained sentence embedding model.

    @lru_cache ensures that the model is loaded only once while
    the Flask application is running.
    """

    print("MEDTRUST AI: Loading semantic model...")

    model = SentenceTransformer(MODEL_NAME)

    print("MEDTRUST AI: Semantic model loaded.")

    return model


# ============================================================
# TEXT PREPARATION
# ============================================================

def build_evidence_text(evidence_record):
    """
    Combine important evidence fields into one searchable text.
    """

    topic = evidence_record.get("topic", "")
    evidence = evidence_record.get("evidence", "")

    return f"{topic}. {evidence}".strip()


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

def semantic_similarity(claim_text, evidence_text):
    """
    Calculate cosine similarity between a claim and evidence.

    Returns:
        float between approximately 0 and 1
    """

    if not claim_text or not claim_text.strip():
        return 0.0

    if not evidence_text or not evidence_text.strip():
        return 0.0

    model = get_model()

    claim_embedding = model.encode(
        claim_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    evidence_embedding = model.encode(
        evidence_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarity = util.cos_sim(
        claim_embedding,
        evidence_embedding
    ).item()

    # Keep the value within a clean range for our UI.
    similarity = max(0.0, min(1.0, similarity))

    return round(similarity, 4)


# ============================================================
# RANK EVIDENCE
# ============================================================

def rank_evidence_semantically(claim_text, evidence_records, top_k=5):
    """
    Rank evidence records according to semantic similarity.

    Each returned record receives:

        semantic_score

    The original evidence information is preserved.
    """

    if not claim_text or not evidence_records:
        return []

    model = get_model()

    claim_embedding = model.encode(
        claim_text,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    evidence_texts = [
        build_evidence_text(record)
        for record in evidence_records
    ]

    evidence_embeddings = model.encode(
        evidence_texts,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        claim_embedding,
        evidence_embeddings
    )[0]

    ranked_results = []

    for index, record in enumerate(evidence_records):

        score = float(similarities[index].item())

        score = max(0.0, min(1.0, score))

        result = dict(record)

        result["semantic_score"] = round(score, 4)

        ranked_results.append(result)

    ranked_results.sort(
        key=lambda item: item["semantic_score"],
        reverse=True
    )

    return ranked_results[:top_k]


# ============================================================
# SEMANTIC SEARCH
# ============================================================

def semantic_search(
    claim_text,
    evidence_database,
    top_k=5,
    minimum_score=0.25
):
    """
    Perform semantic retrieval over the complete evidence database.

    Evidence below minimum_score is ignored.

    NOTE:
        The threshold is a retrieval threshold, not a medical
        correctness threshold.
    """

    if not claim_text or not claim_text.strip():
        return []

    if not evidence_database:
        return []

    ranked = rank_evidence_semantically(
        claim_text,
        evidence_database,
        top_k=top_k
    )

    filtered = [
        item
        for item in ranked
        if item.get("semantic_score", 0.0) >= minimum_score
    ]

    return filtered


# ============================================================
# DEBUG / TEST
# ============================================================

if __name__ == "__main__":

    test_evidence = [
        {
            "id": "AB001",
            "topic": "Antibiotics and viral infections",
            "evidence": (
                "Antibiotics do not work against viruses and should "
                "not be used to treat viral illnesses."
            )
        },
        {
            "id": "VC001",
            "topic": "Vitamin C and common cold",
            "evidence": (
                "Vitamin C does not appear to reduce the chance of "
                "getting a common cold in the general population."
            )
        },
        {
            "id": "HY001",
            "topic": "Hydration",
            "evidence": (
                "Adequate fluid intake helps maintain normal hydration."
            )
        }
    ]

    test_claims = [
        "Taking antibiotics will not help when the illness is caused by a virus.",
        "Drinking enough water helps prevent dehydration.",
        "Vitamin C can affect the duration of a cold."
    ]

    print("\n")
    print("=" * 70)
    print("MEDTRUST AI - SEMANTIC RETRIEVAL TEST")
    print("=" * 70)

    for claim in test_claims:

        print("\nCLAIM:")
        print(claim)

        results = semantic_search(
            claim,
            test_evidence,
            top_k=3
        )

        print("\nSEMANTIC RESULTS:")

        for result in results:

            print(
                f"- {result['id']} | "
                f"{result['topic']} | "
                f"semantic_score="
                f"{result['semantic_score']}"
            )