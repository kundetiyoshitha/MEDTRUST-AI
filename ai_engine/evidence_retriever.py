"""
MEDTRUST AI - Hybrid Evidence Retriever

MEDTRUST AI uses:
    1. Keyword matching
    2. Machine-learning semantic similarity
    3. A conservative relevance gate

Important safety rule:
Weak or unrelated evidence must NOT be presented as
trusted medical evidence.

Safety rules are handled separately from medical evidence.
"""

from ai_engine.semantic_retriever import semantic_search


# ============================================================
# TRUSTED EVIDENCE DATABASE
# ============================================================

EVIDENCE_DATABASE = [

    # --------------------------------------------------------
    # VITAMIN C
    # --------------------------------------------------------

    {
        "id": "VC001",
        "topic": "Vitamin C",
        "evidence": (
            "Vitamin C supplements do not appear to reduce the risk "
            "of getting the common cold in the general population, "
            "although regular supplementation may slightly reduce "
            "the duration or severity of colds."
        ),
        "source": "NIH Office of Dietary Supplements",
        "source_type": "NIH",
        "strength": "Strong",
        "keywords": [
            "vitamin c",
            "common cold",
            "cold",
            "supplement",
            "prevention"
        ]
    },

    {
        "id": "VC002",
        "topic": "Vitamin C Safety",
        "evidence": (
            "High doses of vitamin C supplements can cause diarrhea, "
            "nausea, and stomach cramps. The tolerable upper intake "
            "level for adults is 2,000 mg per day."
        ),
        "source": "NIH Office of Dietary Supplements",
        "source_type": "NIH",
        "strength": "Strong",
        "keywords": [
            "vitamin c",
            "dose",
            "dosage",
            "high dose",
            "safety",
            "side effects"
        ]
    },


    # --------------------------------------------------------
    # ANTIBIOTICS
    # --------------------------------------------------------

    {
        "id": "AB001",
        "topic": "Antibiotics",
        "evidence": (
            "Antibiotics do not work against viruses and should not "
            "be used to treat viral infections such as colds or flu."
        ),
        "source": "Centers for Disease Control and Prevention",
        "source_type": "CDC",
        "strength": "Strong",
        "keywords": [
            "antibiotics",
            "antibiotic",
            "virus",
            "viral",
            "cold",
            "flu",
            "infection"
        ]
    },

    {
        "id": "AB002",
        "topic": "Antibiotic Resistance",
        "evidence": (
            "Using antibiotics when they are not needed can contribute "
            "to antibiotic resistance and can expose people to "
            "unnecessary side effects."
        ),
        "source": "Centers for Disease Control and Prevention",
        "source_type": "CDC",
        "strength": "Strong",
        "keywords": [
            "antibiotics",
            "antibiotic resistance",
            "resistance",
            "side effects",
            "unnecessary"
        ]
    },


    # --------------------------------------------------------
    # HYDRATION
    # --------------------------------------------------------

    {
        "id": "HY001",
        "topic": "Hydration",
        "evidence": (
            "Drinking enough water helps maintain normal hydration. "
            "Water needs vary depending on factors such as activity, "
            "environment, age, and health status."
        ),
        "source": "MedlinePlus",
        "source_type": "MedlinePlus",
        "strength": "Strong",
        "keywords": [
            "water",
            "hydration",
            "dehydration",
            "drink",
            "fluid"
        ]
    },


    # --------------------------------------------------------
    # HYPERTENSION
    # --------------------------------------------------------

    {
        "id": "BP001",
        "topic": "Hypertension",
        "evidence": (
            "Hypertension is high blood pressure and is a major risk "
            "factor for cardiovascular disease. Healthy lifestyle "
            "changes can help prevent or manage high blood pressure."
        ),
        "source": "World Health Organization",
        "source_type": "WHO",
        "strength": "Strong",
        "keywords": [
            "hypertension",
            "high blood pressure",
            "blood pressure",
            "cardiovascular",
            "heart disease"
        ]
    },


    # --------------------------------------------------------
    # DIABETES
    # --------------------------------------------------------

    {
        "id": "DM001",
        "topic": "Diabetes",
        "evidence": (
            "Diabetes is a chronic condition in which blood glucose "
            "levels are elevated. Healthy eating, physical activity, "
            "and appropriate medical care can help manage diabetes."
        ),
        "source": "World Health Organization",
        "source_type": "WHO",
        "strength": "Strong",
        "keywords": [
            "diabetes",
            "blood glucose",
            "blood sugar",
            "glucose",
            "insulin"
        ]
    },


    # --------------------------------------------------------
    # FEVER
    # --------------------------------------------------------

    {
        "id": "FEVER001",
        "topic": "Fever",
        "evidence": (
            "Fever is a temporary increase in body temperature that "
            "can occur as part of the body's response to infection "
            "or other conditions."
        ),
        "source": "MedlinePlus",
        "source_type": "MedlinePlus",
        "strength": "Strong",
        "keywords": [
            "fever",
            "temperature",
            "body temperature",
            "infection"
        ]
    },


    # --------------------------------------------------------
    # HEADACHE
    # --------------------------------------------------------

    {
        "id": "HEAD001",
        "topic": "Headache",
        "evidence": (
            "Headaches can have many different causes. Common types "
            "include tension headaches and migraine. Severe or unusual "
            "headaches may require medical evaluation."
        ),
        "source": "MedlinePlus",
        "source_type": "MedlinePlus",
        "strength": "Strong",
        "keywords": [
            "headache",
            "head pain",
            "migraine",
            "pain"
        ]
    },


    # --------------------------------------------------------
    # SLEEP
    # --------------------------------------------------------

    {
        "id": "SLEEP001",
        "topic": "Sleep",
        "evidence": (
            "Adequate sleep is important for physical and mental health. "
            "Sleep needs vary by age, and poor sleep can affect health "
            "and daily functioning."
        ),
        "source": "National Heart, Lung, and Blood Institute",
        "source_type": "NIH",
        "strength": "Strong",
        "keywords": [
            "sleep",
            "sleeping",
            "insomnia",
            "rest",
            "sleep health"
        ]
    },


    # --------------------------------------------------------
    # PHYSICAL ACTIVITY
    # --------------------------------------------------------

    {
        "id": "EX001",
        "topic": "Physical Activity",
        "evidence": (
            "Regular physical activity provides health benefits and "
            "can reduce the risk of several chronic diseases."
        ),
        "source": "World Health Organization",
        "source_type": "WHO",
        "strength": "Strong",
        "keywords": [
            "exercise",
            "physical activity",
            "fitness",
            "walking",
            "activity"
        ]
    },


    # --------------------------------------------------------
    # MENTAL HEALTH
    # --------------------------------------------------------

    {
        "id": "MW001",
        "topic": "Mental Health",
        "evidence": (
            "Mental health is an important component of overall health "
            "and well-being. Mental health conditions can affect "
            "thoughts, emotions, behavior, and daily functioning."
        ),
        "source": "World Health Organization",
        "source_type": "WHO",
        "strength": "Strong",
        "keywords": [
            "mental health",
            "stress",
            "anxiety",
            "wellbeing",
            "well-being",
            "depression"
        ]
    },


    # --------------------------------------------------------
    # MEDICATION SAFETY
    # --------------------------------------------------------

    {
        "id": "MED001",
        "topic": "Medication Safety",
        "evidence": (
            "Medication should be used according to appropriate "
            "instructions. Patients should not change or stop prescribed "
            "medications without consulting a healthcare professional."
        ),
        "source": "U.S. Food and Drug Administration",
        "source_type": "FDA",
        "strength": "Strong",
        "keywords": [
            "medication",
            "medicine",
            "drug",
            "dose",
            "prescription",
            "stop medication"
        ]
    },


    # --------------------------------------------------------
    # MEDTRUST SAFETY RULE
    #
    # IMPORTANT:
    # This is NOT medical evidence.
    # It is handled separately below.
    # --------------------------------------------------------

    {
        "id": "SAFE001",
        "topic": "Medical Safety",
        "evidence": (
            "Absolute medical claims such as guaranteed cures, "
            "complete prevention, or statements that a treatment "
            "always works require strong evidence and should be "
            "treated cautiously."
        ),
        "source": "MEDTRUST AI Safety Rules",
        "source_type": "MEDTRUST",
        "strength": "Safety Rule",
        "keywords": [
            "cure",
            "prevents",
            "prevent",
            "guaranteed",
            "guarantee",
            "always",
            "never",
            "completely",
            "100%"
        ]
    }
]


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(text):
    """
    Normalize text for keyword matching.
    """

    return " ".join(
        (text or "").lower().split()
    )


def _keyword_score(query, item):
    """
    Calculate keyword overlap.

    The score is normalized between 0 and 1.
    """

    query_text = normalize_text(query)

    if not query_text:
        return 0.0

    keywords = item.get("keywords", [])

    if not keywords:
        return 0.0

    matched = 0

    for keyword in keywords:

        if keyword.lower() in query_text:
            matched += 1

    # Normalize while avoiding very small scores
    score = matched / max(len(keywords) * 0.35, 1)

    return min(score, 1.0)


def _matched_keywords(query, item):
    """
    Return keywords found directly in the query.
    """

    query_text = normalize_text(query)

    return [
        keyword
        for keyword in item.get("keywords", [])
        if keyword.lower() in query_text
    ]


# ============================================================
# HYBRID SCORE
# ============================================================

def _combine_scores(keyword_score, semantic_score):
    """
    Combine keyword and ML semantic scores.

    Semantic similarity receives slightly more weight.
    """

    keyword_score = float(
        keyword_score or 0
    )

    semantic_score = float(
        semantic_score or 0
    )

    return (
        (0.40 * keyword_score)
        +
        (0.60 * semantic_score)
    )


# ============================================================
# CONSERVATIVE RELEVANCE GATE
# ============================================================

def _is_strong_enough(
    keyword_score,
    semantic_score,
    combined_score
):
    """
    Decide whether evidence is relevant enough to be returned.

    This is deliberately conservative.

    Example:

        Semantic = 0.30
        Keyword  = 0.00
        Combined  = 0.18

    Result:

        REJECT

    This prevents unrelated evidence from being shown as
    trusted evidence.
    """

    keyword_score = float(
        keyword_score or 0
    )

    semantic_score = float(
        semantic_score or 0
    )

    combined_score = float(
        combined_score or 0
    )

    # --------------------------------------------------------
    # Rule 1: Strong combined match
    # --------------------------------------------------------

    if combined_score >= 0.55:
        return True

    # --------------------------------------------------------
    # Rule 2: Strong semantic match + keyword connection
    # --------------------------------------------------------

    if (
        semantic_score >= 0.65
        and
        keyword_score >= 0.15
    ):
        return True

    # --------------------------------------------------------
    # Rule 3: Very strong direct keyword match
    # --------------------------------------------------------

    if keyword_score >= 0.65:
        return True

    return False


# ============================================================
# MEDICAL EVIDENCE RETRIEVAL
# ============================================================

def retrieve_evidence(query, top_k=5):
    """
    Retrieve trusted medical evidence using hybrid retrieval.

    Safety rules are excluded from this function because they
    are not medical evidence.
    """

    if not query or not query.strip():
        return []

    query = query.strip()

    # --------------------------------------------------------
    # Run semantic search over the complete database
    # --------------------------------------------------------

    semantic_results = semantic_search(
        query,
        EVIDENCE_DATABASE,
        top_k=len(EVIDENCE_DATABASE)
    )

    # --------------------------------------------------------
    # Create lookup table
    # --------------------------------------------------------

    semantic_lookup = {
        item.get("id"): item
        for item in semantic_results
    }

    results = []

    # --------------------------------------------------------
    # Score every evidence item
    # --------------------------------------------------------

    for item in EVIDENCE_DATABASE:

        # ----------------------------------------------------
        # IMPORTANT:
        # Safety rules are NOT medical evidence.
        # ----------------------------------------------------

        if item.get("id", "").startswith("SAFE"):
            continue

        semantic_item = semantic_lookup.get(
            item["id"],
            {}
        )

        semantic_score = float(
            semantic_item.get(
                "semantic_score",
                0
            ) or 0
        )

        keyword_score = _keyword_score(
            query,
            item
        )

        combined_score = _combine_scores(
            keyword_score,
            semantic_score
        )

        matched_keywords = _matched_keywords(
            query,
            item
        )

        # ----------------------------------------------------
        # CONSERVATIVE SAFETY GATE
        # ----------------------------------------------------

        if not _is_strong_enough(
            keyword_score,
            semantic_score,
            combined_score
        ):
            continue

        results.append({
            "id": item["id"],
            "topic": item["topic"],
            "evidence": item["evidence"],
            "source": item["source"],
            "source_type": item["source_type"],
            "strength": item["strength"],
            "relevance_score": round(
                combined_score,
                3
            ),
            "keyword_score": round(
                keyword_score,
                3
            ),
            "semantic_score": round(
                semantic_score,
                3
            ),
            "matched_keywords": matched_keywords
        })

    # --------------------------------------------------------
    # Highest relevance first
    # --------------------------------------------------------

    results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

    return results[:top_k]


# ============================================================
# SAFETY FLAGS
# ============================================================

def retrieve_safety_flags(query):
    """
    Detect safety-related wording separately from medical evidence.

    These flags are used by the risk engine.
    They are NOT presented as medical evidence.
    """

    if not query:
        return []

    query_text = normalize_text(query)

    absolute_terms = [
        "completely",
        "always",
        "never",
        "guaranteed",
        "guarantee",
        "100%",
        "cure",
        "prevents",
        "prevent"
    ]

    matched_terms = [
        term
        for term in absolute_terms
        if term in query_text
    ]

    if not matched_terms:
        return []

    return [
        {
            "id": "SAFE001",
            "topic": "Medical Safety",
            "evidence": (
                "Absolute medical claims require strong evidence "
                "and should be treated cautiously."
            ),
            "source": "MEDTRUST AI Safety Rules",
            "source_type": "MEDTRUST",
            "strength": "Safety Rule",
            "matched_keywords": matched_terms
        }
    ]


# ============================================================
# COMPLETE CLAIM RETRIEVAL
# ============================================================

def retrieve_for_claim(claim):
    """
    Retrieve medical evidence and safety flags separately.
    """

    return {
        "medical_evidence": retrieve_evidence(
            claim
        ),

        "safety_flags": retrieve_safety_flags(
            claim
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("MEDTRUST AI - HYBRID RETRIEVER TEST")
    print("-----------------------------------")

    test_queries = [

        "Vitamin C completely prevents the common cold.",

        "Drinking enough water helps maintain hydration.",

        "Is iron deficiency related to heart issues?"
    ]

    for query in test_queries:

        print()
        print("QUERY:")
        print(query)

        results = retrieve_evidence(query)

        print(
            "MEDICAL EVIDENCE COUNT:",
            len(results)
        )

        if not results:
            print("No sufficiently relevant evidence found.")

        for result in results:

            print(
                "-",
                result["topic"],
                "| combined=",
                f"{result['relevance_score']:.2f}",
                "| semantic=",
                f"{result['semantic_score']:.2f}",
                "| keyword=",
                f"{result['keyword_score']:.2f}"
            )

        flags = retrieve_safety_flags(query)

        print(
            "SAFETY FLAGS:",
            len(flags)
        )

        for flag in flags:
            print(
                "-",
                flag["topic"],
                "|",
                flag["matched_keywords"]
            )