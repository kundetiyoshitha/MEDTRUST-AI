"""
MEDTRUST AI - Claim Verification

Conservative evidence-based verification.

The verifier accepts both:
    1. A list of medical evidence
    2. The complete retrieve_for_claim() dictionary

This keeps compatibility with the MEDTRUST pipeline.
"""

import re


SUPPORTED = "SUPPORTED"
CONTRADICTED = "CONTRADICTED"
UNCERTAIN = "UNCERTAIN"


def _clean(text):
    """Normalize text for comparison."""
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _is_relevant_evidence(evidence):
    """
    Reject weak or unrelated evidence.

    Evidence must have enough semantic/keyword relevance
    before it can influence the verification decision.
    """

    if not isinstance(evidence, dict):
        return False

    relevance = float(
        evidence.get("relevance_score", 0) or 0
    )

    semantic = float(
        evidence.get("semantic_score", 0) or 0
    )

    keyword = float(
        evidence.get("keyword_score", 0) or 0
    )

    # Strong overall relevance
    if relevance >= 0.45:
        return True

    # Strong semantic match + some keyword connection
    if semantic >= 0.55 and keyword >= 0.15:
        return True

    # Strong keyword match
    if keyword >= 0.50:
        return True

    return False


def _contains_contradiction(claim, evidence_text):
    """
    Detect obvious contradiction patterns.

    This is a safety heuristic, not a medical diagnosis model.
    """

    claim_text = _clean(claim)
    evidence = _clean(evidence_text)

    absolute_terms = [
        "completely",
        "always",
        "never",
        "guaranteed",
        "guarantee",
        "100%",
        "cure",
        "prevents",
    ]

    contradiction_terms = [
        "does not",
        "do not",
        "not proven",
        "no evidence",
        "not recommended",
        "has not been shown",
        "doesn't",
    ]

    claim_is_absolute = any(
        term in claim_text
        for term in absolute_terms
    )

    evidence_contradicts = any(
        term in evidence
        for term in contradiction_terms
    )

    return claim_is_absolute and evidence_contradicts


def _normalize_input(evidence_results):
    """
    Make the verifier compatible with both:

        [
            {...},
            {...}
        ]

    and:

        {
            "medical_evidence": [...],
            "safety_flags": [...]
        }
    """

    safety_flags = []

    # Complete retrieve_for_claim() structure
    if isinstance(evidence_results, dict):

        medical_evidence = evidence_results.get(
            "medical_evidence",
            []
        )

        safety_flags = evidence_results.get(
            "safety_flags",
            []
        )

        if not isinstance(medical_evidence, list):
            medical_evidence = []

        if not isinstance(safety_flags, list):
            safety_flags = []

        return medical_evidence, safety_flags

    # Direct list of evidence
    if isinstance(evidence_results, list):
        return evidence_results, safety_flags

    return [], safety_flags


def verify_claim(claim, evidence_results=None):
    """
    Verify a healthcare claim using trusted evidence.

    Returns a structure compatible with the MEDTRUST pipeline.
    """

    medical_evidence, safety_flags = _normalize_input(
        evidence_results
    )

    # ---------------------------------------------------------
    # SAFETY RELEVANCE GATE
    # ---------------------------------------------------------

    relevant_evidence = [
        item
        for item in medical_evidence
        if _is_relevant_evidence(item)
    ]

    # ---------------------------------------------------------
    # NO TRUSTWORTHY EVIDENCE
    # ---------------------------------------------------------

    if not relevant_evidence:

        return {
            "status": UNCERTAIN,
            "confidence": 10,

            "reason": (
                "No sufficiently relevant trusted evidence was "
                "found for this claim. MEDTRUST AI cannot verify "
                "it safely."
            ),

            # Keep these fields for pipeline compatibility
            "medical_evidence": [],
            "safety_flags": safety_flags,

            # Also keep generic evidence field
            "evidence": []
        }

    # ---------------------------------------------------------
    # CONTRADICTION CHECK
    # ---------------------------------------------------------

    contradiction_found = False

    for item in relevant_evidence:

        evidence_text = item.get(
            "evidence",
            ""
        )

        if _contains_contradiction(
            claim,
            evidence_text
        ):
            contradiction_found = True
            break

    if contradiction_found:

        return {
            "status": CONTRADICTED,
            "confidence": 85,

            "reason": (
                "Relevant trusted evidence was found, but it "
                "conflicts with the claim or does not support "
                "the claim's absolute wording."
            ),

            "medical_evidence": relevant_evidence,
            "safety_flags": safety_flags,
            "evidence": relevant_evidence
        }

    # ---------------------------------------------------------
    # STRONG EVIDENCE
    # ---------------------------------------------------------

    strongest = max(
        relevant_evidence,
        key=lambda item: float(
            item.get(
                "relevance_score",
                0
            ) or 0
        )
    )

    strongest_score = float(
        strongest.get(
            "relevance_score",
            0
        ) or 0
    )

    if strongest_score >= 0.60:

        return {
            "status": SUPPORTED,
            "confidence": 75,

            "reason": (
                "Relevant trusted medical evidence was found "
                "and no direct contradiction was detected."
            ),

            "medical_evidence": relevant_evidence,
            "safety_flags": safety_flags,
            "evidence": relevant_evidence
        }

    # ---------------------------------------------------------
    # PARTIAL / UNCERTAIN EVIDENCE
    # ---------------------------------------------------------

    return {
        "status": UNCERTAIN,
        "confidence": 50,

        "reason": (
            "Some potentially relevant evidence was found, "
            "but the available evidence is not strong enough "
            "for confident verification."
        ),

        "medical_evidence": relevant_evidence,
        "safety_flags": safety_flags,
        "evidence": relevant_evidence
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\nMEDTRUST AI - VERIFIER TEST")
    print("---------------------------")

    claim = (
        "Vitamin C completely prevents the common cold."
    )

    evidence = {
        "medical_evidence": [
            {
                "topic": "Vitamin C",
                "evidence": (
                    "Vitamin C does not appear to prevent "
                    "the common cold in the general population."
                ),
                "source": (
                    "NIH Office of Dietary Supplements"
                ),
                "relevance_score": 0.82,
                "semantic_score": 0.84,
                "keyword_score": 0.72
            }
        ],
        "safety_flags": []
    }

    result = verify_claim(
        claim,
        evidence
    )

    print("Claim:", claim)
    print("Status:", result["status"])
    print("Confidence:", result["confidence"])
    print("Reason:", result["reason"])
    print(
        "Medical Evidence:",
        len(result["medical_evidence"])
    )