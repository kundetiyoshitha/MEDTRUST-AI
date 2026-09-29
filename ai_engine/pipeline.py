"""
MEDTRUST AI - Core Analysis Pipeline

Detect -> Verify -> Assess -> Mitigate
"""

from ai_engine.claim_extractor import extract_claims
from ai_engine.evidence_retriever import retrieve_evidence
from ai_engine.verifier import verify_claim
from ai_engine.risk_analyzer import analyze_risk
from ai_engine.mitigation import mitigate_claim


def _count_evidence(results):
    return sum(len(item.get("evidence", [])) for item in results)


def _detect_topics(results):
    topics = []

    for item in results:
        for evidence in item.get("evidence", []):
            topic = evidence.get("topic")

            if topic and topic not in topics:
                topics.append(topic)

    return topics


def _recommendation(
    supported,
    uncertain,
    contradicted,
    high,
    critical,
    total
):
    if critical:
        return (
            "Do not rely on the flagged high-risk content. "
            "Human review is required before the information is used."
        )

    if high:
        return (
            "Human review is recommended before relying on "
            "the high-risk content."
        )

    if contradicted:
        return (
            "Potentially hallucinated claims were detected. "
            "Review the highlighted claims against the cited evidence."
        )

    if uncertain:
        return (
            "Some claims could not be sufficiently verified. "
            "Review the available evidence before relying on the response."
        )

    if total and supported == total:
        return (
            "The analyzed claims were supported by the retrieved evidence. "
            "Continue to use appropriate professional judgment."
        )

    return (
        "Insufficient evidence was available to confidently "
        "assess the complete response."
    )


def _empty_result(message, status="NO RESPONSE"):
    summary = {
        "topic": message,
        "topics": [],
        "claims_detected": 0,
        "evidence_found": 0,
        "supported": 0,
        "uncertain": 0,
        "contradicted": 0,
        "high_risk": 0,
        "critical": 0,
        "needs_attention": 0,
        "risk": status,
        "safety_score": 0,
        "recommendation": message,
    }

    return {
        "success": False,
        "response": "",
        "claims": [],
        "total_claims": 0,
        "claims_detected": 0,
        "supported_claims": 0,
        "uncertain_claims": 0,
        "contradicted_claims": 0,
        "high_risk_claims": 0,
        "critical_claims": 0,
        "needs_attention": 0,
        "evidence_found": 0,
        "topics": [],
        "safety_score": 0,
        "overall_status": status,
        "overall_risk": status,
        "human_review_required": False,
        "recommendation": message,
        "summary": summary,
    }


def analyze_response(response):
    """
    Analyze an AI-generated healthcare response.

    Flow:
        Response
        ↓
        Claim Extraction
        ↓
        Evidence Retrieval
        ↓
        Claim Verification
        ↓
        Risk Analysis
        ↓
        Mitigation
        ↓
        Safety Score
    """

    # ---------------------------------------------------------
    # EMPTY RESPONSE
    # ---------------------------------------------------------

    if not response or not response.strip():
        return _empty_result(
            "Provide an AI-generated healthcare response "
            "to begin verification."
        )

    response = response.strip()

    # ---------------------------------------------------------
    # CLAIM EXTRACTION
    # ---------------------------------------------------------

    claims = extract_claims(response)

    if not claims:
        result = _empty_result(
            "The response did not contain enough meaningful "
            "claims to analyze.",
            "NO CLAIMS",
        )

        result["response"] = response

        return result

    results = []

    # ---------------------------------------------------------
    # CLAIM-BY-CLAIM ANALYSIS
    # ---------------------------------------------------------

    for number, claim in enumerate(claims, start=1):

        # Evidence Retrieval
        evidence = retrieve_evidence(claim)

        # Verification
        verification = verify_claim(
            claim,
            evidence
        )

        # Risk Analysis
        risk = analyze_risk(
            claim,
            verification
        )

        # Mitigation
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
            "mitigation": mitigation,
        })

    # ---------------------------------------------------------
    # VERIFICATION COUNTS
    # ---------------------------------------------------------

    supported = sum(
        1
        for item in results
        if str(
            item["verification"].get(
                "status",
                ""
            )
        ).upper() == "SUPPORTED"
    )

    uncertain = sum(
        1
        for item in results
        if str(
            item["verification"].get(
                "status",
                ""
            )
        ).upper() == "UNCERTAIN"
    )

    contradicted = sum(
        1
        for item in results
        if str(
            item["verification"].get(
                "status",
                ""
            )
        ).upper() == "CONTRADICTED"
    )

    # ---------------------------------------------------------
    # RISK COUNTS
    # ---------------------------------------------------------

    high = sum(
        1
        for item in results
        if str(
            item["risk"].get(
                "risk_level",
                ""
            )
        ).upper() == "HIGH"
    )

    critical = sum(
        1
        for item in results
        if str(
            item["risk"].get(
                "risk_level",
                ""
            )
        ).upper() == "CRITICAL"
    )

    # ---------------------------------------------------------
    # SAFETY SCORE
    # ---------------------------------------------------------

    risk_scores = []

    for item in results:

        try:
            score = float(
                item["risk"].get(
                    "risk_score",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):
            score = 0.0

        risk_scores.append(score)

    if risk_scores:

        average_risk = (
            sum(risk_scores)
            / len(risk_scores)
        )

    else:

        average_risk = 0

    safety_score = round(
        max(
            0,
            min(
                100,
                100 - average_risk
            )
        )
    )

    # ---------------------------------------------------------
    # OVERALL STATUS
    # ---------------------------------------------------------

    if critical > 0:

        overall_status = "CRITICAL"

    elif high > 0:

        overall_status = "HIGH RISK"

    elif contradicted > 0:

        overall_status = "POTENTIAL HALLUCINATION"

    elif uncertain > 0:

        overall_status = "NEEDS REVIEW"

    elif supported > 0:

        overall_status = "SUPPORTED"

    else:

        overall_status = "INSUFFICIENT EVIDENCE"

    # ---------------------------------------------------------
    # ADDITIONAL METRICS
    # ---------------------------------------------------------

    evidence_count = _count_evidence(
        results
    )

    topics = _detect_topics(
        results
    )

    needs_attention = (
        uncertain
        + contradicted
        + high
        + critical
    )

    human_review_required = bool(
        high > 0
        or critical > 0
    )

    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    recommendation = _recommendation(
        supported=supported,
        uncertain=uncertain,
        contradicted=contradicted,
        high=high,
        critical=critical,
        total=len(results),
    )

    # ---------------------------------------------------------
    # TOPIC TEXT
    # ---------------------------------------------------------

    if topics:

        topic_text = ", ".join(
            topics[:5]
        )

    else:

        topic_text = (
            "No clear evidence topic identified"
        )

    # ---------------------------------------------------------
    # AUTOMATIC RESPONSE SUMMARY
    # ---------------------------------------------------------

    summary = {
        "topic": topic_text,
        "topics": topics,
        "claims_detected": len(results),
        "evidence_found": evidence_count,
        "supported": supported,
        "uncertain": uncertain,
        "contradicted": contradicted,
        "high_risk": high,
        "critical": critical,
        "needs_attention": needs_attention,
        "risk": overall_status,
        "safety_score": safety_score,
        "recommendation": recommendation,
    }

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    return {
        "success": True,
        "response": response,
        "claims": results,

        "total_claims": len(results),
        "claims_detected": len(results),

        "supported_claims": supported,
        "uncertain_claims": uncertain,
        "contradicted_claims": contradicted,

        "high_risk_claims": high,
        "critical_claims": critical,

        "needs_attention": needs_attention,

        "evidence_found": evidence_count,

        "topics": topics,

        "safety_score": safety_score,

        "overall_status": overall_status,
        "overall_risk": overall_status,

        "human_review_required": (
            human_review_required
        ),

        "recommendation": recommendation,

        "summary": summary,
    }


# =============================================================
# PIPELINE TEST
# =============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("MEDTRUST AI - PIPELINE TEST")
    print("=" * 70)

    test_response = """
    Vitamin C completely prevents the common cold.
    Drinking enough water helps maintain hydration.
    Vitamin C is always completely safe at any dosage.
    Iron deficiency is related to serious heart problems.
    """

    result = analyze_response(
        test_response
    )

    if not result.get("success"):

        print()
        print(
            "ERROR:",
            result.get(
                "recommendation",
                "Analysis failed."
            )
        )

    else:

        print()
        print(
            "Overall Status:",
            result["overall_status"]
        )

        print(
            "Safety Score:",
            f'{result["safety_score"]}/100'
        )

        print(
            "Total Claims:",
            result["total_claims"]
        )

        print(
            "Supported:",
            result["supported_claims"]
        )

        print(
            "Uncertain:",
            result["uncertain_claims"]
        )

        print(
            "Contradicted:",
            result["contradicted_claims"]
        )

        print(
            "High Risk:",
            result["high_risk_claims"]
        )

        print(
            "Critical:",
            result["critical_claims"]
        )

        print(
            "Evidence Found:",
            result["evidence_found"]
        )

        print(
            "Needs Attention:",
            result["needs_attention"]
        )

        print(
            "Human Review:",
            result["human_review_required"]
        )

        print()
        print(
            "Recommendation:",
            result["recommendation"]
        )

        print()
        print("-" * 70)
        print("CLAIM RESULTS")
        print("-" * 70)

        for item in result["claims"]:

            print()
            print(
                f'Claim {item["claim_number"]}:'
            )

            print(
                " ",
                item["claim"]
            )

            print(
                " Verification:",
                item["verification"].get(
                    "status"
                )
            )

            print(
                " Risk:",
                item["risk"].get(
                    "risk_level"
                )
            )

            print(
                " Risk Score:",
                item["risk"].get(
                    "risk_score"
                )
            )

            print(
                " Action:",
                item["mitigation"].get(
                    "action"
                )
            )

            print(
                " Evidence:",
                len(
                    item.get(
                        "evidence",
                        []
                    )
                )
            )

    print()
    print("=" * 70)