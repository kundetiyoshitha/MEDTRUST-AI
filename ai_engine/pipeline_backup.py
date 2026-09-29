from ai_engine.claim_extractor import extract_claims
from ai_engine.evidence_retriever import retrieve_evidence
from ai_engine.verifier import verify_claim
from ai_engine.risk_analyzer import analyze_risk
from ai_engine.mitigation import mitigate_claim


def _detect_topics(claims):
    """
    Create a simple topic summary from retrieved evidence.

    This is intentionally based on evidence retrieved by MEDTRUST,
    rather than guessing a medical diagnosis or condition.
    """

    topics = []

    for item in claims:

        for evidence in item.get("evidence", []):

            topic = evidence.get("topic")

            if topic and topic not in topics:
                topics.append(topic)

    return topics


def _count_evidence(claims):
    """
    Count total evidence records retrieved across all claims.
    """

    count = 0

    for item in claims:
        count += len(item.get("evidence", []))

    return count


def _build_recommendation(
    supported_claims,
    uncertain_claims,
    contradicted_claims,
    high_risk_claims,
    critical_claims,
    total_claims
):
    """
    Generate a concise system-level recommendation.

    This is NOT a medical recommendation to the patient.

    It is a safety recommendation about whether the analyzed
    AI response should be trusted.
    """

    if critical_claims > 0:

        return (
            "Do not rely on the flagged high-risk content. "
            "Human review is required before the information is used."
        )

    if high_risk_claims > 0:

        return (
            "Human review is recommended before relying on the "
            "high-risk content."
        )

    if contradicted_claims > 0:

        return (
            "Potentially hallucinated claims were detected. "
            "Review the highlighted claims against the cited evidence."
        )

    if uncertain_claims > 0:

        return (
            "Some claims could not be sufficiently verified. "
            "Review the available evidence before relying on the response."
        )

    if total_claims > 0 and supported_claims == total_claims:

        return (
            "The analyzed claims were supported by the retrieved evidence. "
            "Continue to use appropriate professional judgment."
        )

    return (
        "Insufficient evidence was available to confidently assess "
        "the complete response."
    )


def _build_response_summary(
    response,
    claims,
    topics,
    evidence_count,
    supported_claims,
    uncertain_claims,
    contradicted_claims,
    high_risk_claims,
    critical_claims,
    safety_score,
    overall_status
):
    """
    Build the automatic summary displayed to the user.

    Example:

        Topic:
            Vitamin C and common cold

        Claims detected:
            4

        Evidence found:
            5

        Risk:
            HIGH

        Needs attention:
            2

        Recommendation:
            Review highlighted claims.
    """

    needs_attention = (
        uncertain_claims
        + contradicted_claims
        + high_risk_claims
        + critical_claims
    )

    recommendation = _build_recommendation(
        supported_claims=supported_claims,
        uncertain_claims=uncertain_claims,
        contradicted_claims=contradicted_claims,
        high_risk_claims=high_risk_claims,
        critical_claims=critical_claims,
        total_claims=len(claims)
    )

    if topics:

        topic_text = ", ".join(topics[:5])

        if len(topics) > 5:
            topic_text += ", and more"

    else:

        topic_text = "No clear evidence topic identified"

    return {
        "topic": topic_text,
        "topics": topics,
        "claims_detected": len(claims),
        "evidence_found": evidence_count,
        "supported": supported_claims,
        "uncertain": uncertain_claims,
        "contradicted": contradicted_claims,
        "high_risk": high_risk_claims,
        "critical": critical_claims,
        "needs_attention": needs_attention,
        "risk": overall_status,
        "safety_score": safety_score,
        "recommendation": recommendation
    }


def analyze_response(response):
    """
    Complete MEDTRUST AI safety pipeline.

    Flow:

        Response
            ↓
        Claim Extraction
            ↓
        Hybrid Evidence Retrieval
            ├── Keyword matching
            └── ML semantic similarity
            ↓
        Verification
            ↓
        Risk Analysis
            ↓
        Mitigation
            ↓
        Automatic Response Summary
    """

    # --------------------------------------------------
    # EMPTY RESPONSE
    # --------------------------------------------------

    if not response or not response.strip():

        return {
            "response": response,
            "claims": [],
            "total_claims": 0,
            "supported_claims": 0,
            "uncertain_claims": 0,
            "contradicted_claims": 0,
            "high_risk_claims": 0,
            "critical_claims": 0,
            "safety_score": 0,
            "overall_status": "NO RESPONSE",
            "summary": {
                "topic": "No response provided",
                "topics": [],
                "claims_detected": 0,
                "evidence_found": 0,
                "supported": 0,
                "uncertain": 0,
                "contradicted": 0,
                "high_risk": 0,
                "critical": 0,
                "needs_attention": 0,
                "risk": "NO RESPONSE",
                "safety_score": 0,
                "recommendation": (
                    "Provide an AI-generated healthcare response "
                    "to begin verification."
                )
            }
        }

    # --------------------------------------------------
    # STEP 1 — EXTRACT CLAIMS
    # --------------------------------------------------

    claims = extract_claims(response)

    results = []

    # --------------------------------------------------
    # STEP 2 — ANALYZE EVERY CLAIM
    # --------------------------------------------------

    for number, claim in enumerate(claims, start=1):

        # ----------------------------------------------
        # Hybrid evidence retrieval
        #
        # The upgraded retriever combines:
        #   keyword relevance
        #   ML semantic relevance
        # ----------------------------------------------

        evidence = retrieve_evidence(claim)

        # ----------------------------------------------
        # Verification
        # ----------------------------------------------

        verification = verify_claim(
            claim,
            evidence
        )

        # ----------------------------------------------
        # Risk analysis
        # ----------------------------------------------

        risk = analyze_risk(
            claim,
            verification
        )

        # ----------------------------------------------
        # Mitigation
        # ----------------------------------------------

        mitigation = mitigate_claim(
            claim,
            verification,
            risk
        )

        results.append({
            "claim_number": number,
            "claim": claim,
            "evidence": evidence,
            "verification": verification,
            "risk": risk,
            "mitigation": mitigation
        })

    # --------------------------------------------------
    # STEP 3 — COUNT VERIFICATION RESULTS
    # --------------------------------------------------

    supported_claims = sum(
        1
        for item in results
        if item["verification"]["status"] == "SUPPORTED"
    )

    uncertain_claims = sum(
        1
        for item in results
        if item["verification"]["status"] == "UNCERTAIN"
    )

    contradicted_claims = sum(
        1
        for item in results
        if item["verification"]["status"] == "CONTRADICTED"
    )

    # --------------------------------------------------
    # STEP 4 — COUNT RISK LEVELS
    # --------------------------------------------------

    high_risk_claims = sum(
        1
        for item in results
        if item["risk"]["risk_level"] == "HIGH"
    )

    critical_claims = sum(
        1
        for item in results
        if item["risk"]["risk_level"] == "CRITICAL"
    )

    # --------------------------------------------------
    # STEP 5 — SAFETY SCORE
    # --------------------------------------------------

    if not results:

        safety_score = 0

    else:

        risk_scores = [
            item["risk"]["risk_score"]
            for item in results
        ]

        average_risk = (
            sum(risk_scores)
            / len(risk_scores)
        )

        safety_score = round(
            max(0, min(100, 100 - average_risk))
        )

    # --------------------------------------------------
    # STEP 6 — OVERALL STATUS
    # --------------------------------------------------

    if critical_claims > 0:

        overall_status = "CRITICAL"

    elif high_risk_claims > 0:

        overall_status = "HIGH RISK"

    elif contradicted_claims > 0:

        overall_status = "POTENTIAL HALLUCINATION"

    elif uncertain_claims > 0:

        overall_status = "NEEDS REVIEW"

    elif supported_claims > 0:

        overall_status = "SUPPORTED"

    else:

        overall_status = "INSUFFICIENT EVIDENCE"

    # --------------------------------------------------
    # STEP 7 — EVIDENCE COUNT
    # --------------------------------------------------

    evidence_count = _count_evidence(
        results
    )

    # --------------------------------------------------
    # STEP 8 — TOPICS
    # --------------------------------------------------

    topics = _detect_topics(
        results
    )

    # --------------------------------------------------
    # STEP 9 — AUTOMATIC RESPONSE SUMMARY
    # --------------------------------------------------

    summary = _build_response_summary(
        response=response,
        claims=results,
        topics=topics,
        evidence_count=evidence_count,
        supported_claims=supported_claims,
        uncertain_claims=uncertain_claims,
        contradicted_claims=contradicted_claims,
        high_risk_claims=high_risk_claims,
        critical_claims=critical_claims,
        safety_score=safety_score,
        overall_status=overall_status
    )

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    return {
        "response": response,

        "claims": results,

        "total_claims": len(results),

        "supported_claims": supported_claims,

        "uncertain_claims": uncertain_claims,

        "contradicted_claims": contradicted_claims,

        "high_risk_claims": high_risk_claims,

        "critical_claims": critical_claims,

        "safety_score": safety_score,

        "overall_status": overall_status,

        "summary": summary
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_response = """
    Vitamin C completely prevents the common cold.
    Drinking enough water can help maintain normal hydration.
    Taking 5000 mg of vitamin C every day is safe for everyone.
    Eating mangoes completely cures hypertension.
    """

    result = analyze_response(
        test_response
    )

    print("\n")
    print("=" * 75)
    print("MEDTRUST AI — COMPLETE SAFETY ANALYSIS")
    print("=" * 75)

    print(
        f"\nOverall Status: "
        f"{result['overall_status']}"
    )

    print(
        f"Safety Score: "
        f"{result['safety_score']}/100"
    )

    print(
        f"Total Claims: "
        f"{result['total_claims']}"
    )

    print(
        f"Supported: "
        f"{result['supported_claims']}"
    )

    print(
        f"Uncertain: "
        f"{result['uncertain_claims']}"
    )

    print(
        f"Contradicted: "
        f"{result['contradicted_claims']}"
    )

    print(
        f"High Risk: "
        f"{result['high_risk_claims']}"
    )

    print(
        f"Critical: "
        f"{result['critical_claims']}"
    )

    print("\n")
    print("=" * 75)
    print("AUTOMATIC RESPONSE SUMMARY")
    print("=" * 75)

    summary = result["summary"]

    print(
        f"\nTopic: "
        f"{summary['topic']}"
    )

    print(
        f"Claims detected: "
        f"{summary['claims_detected']}"
    )

    print(
        f"Evidence found: "
        f"{summary['evidence_found']}"
    )

    print(
        f"Needs attention: "
        f"{summary['needs_attention']}"
    )

    print(
        f"Risk: "
        f"{summary['risk']}"
    )

    print(
        f"Recommendation: "
        f"{summary['recommendation']}"
    )

    print("\n")
    print("=" * 75)
    print("CLAIM-LEVEL RESULTS")
    print("=" * 75)

    for item in result["claims"]:

        print(
            f"\nClaim {item['claim_number']}: "
            f"{item['claim']}"
        )

        print(
            f"Verification: "
            f"{item['verification']['status']}"
        )

        print(
            f"Risk: "
            f"{item['risk']['risk_level']} "
            f"({item['risk']['risk_score']}/100)"
        )

        print(
            f"Action: "
            f"{item['mitigation']['action']}"
        )

        print(
            f"Safety Status: "
            f"{item['mitigation']['safe_status']}"
        )

        print(
            f"Evidence Retrieved: "
            f"{len(item['evidence'])}"
        )

        if item["evidence"]:

            best = item["evidence"][0]

            print(
                f"Best Evidence: "
                f"{best['id']}"
            )

            print(
                f"Keyword Score: "
                f"{best.get('keyword_score', 0)}"
            )

            print(
                f"Semantic Score: "
                f"{best.get('semantic_score', 0)}"
            )

            print(
                f"Combined Score: "
                f"{best.get('relevance_score', 0)}"
            )

        print("-" * 75)