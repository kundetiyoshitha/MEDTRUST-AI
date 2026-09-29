def analyze_risk(claim, verification_result):
    """
    Estimate the potential risk of a healthcare claim.

    Risk levels:
        LOW
        MODERATE
        HIGH
        CRITICAL
    """

    if not claim or not claim.strip():
        return {
            "risk_level": "LOW",
            "risk_score": 0,
            "reason": "No claim was provided.",
            "human_review": False
        }

    claim_lower = claim.lower()

    status = verification_result.get(
        "status",
        "UNCERTAIN"
    )

    safety_flags = verification_result.get(
        "safety_flags",
        []
    )

    score = 0
    risk_reasons = []

    # --------------------------------------------------
    # 1. Verification status
    # --------------------------------------------------

    if status == "CONTRADICTED":
        score += 35
        risk_reasons.append(
            "The claim conflicts with retrieved medical evidence."
        )

    elif status == "UNCERTAIN":
        score += 15
        risk_reasons.append(
            "The claim could not be confidently verified."
        )

    elif status == "SUPPORTED":
        score += 0

    # --------------------------------------------------
    # 2. High-risk medical language
    # --------------------------------------------------

    high_risk_terms = [
        "stop taking",
        "stop your medication",
        "discontinue medication",
        "replace medication",
        "skip medication",
        "change your dose",
        "increase your dose",
        "decrease your dose",
        "take extra",
        "overdose",
        "emergency",
        "life threatening",
        "life-threatening"
    ]

    matched_high_risk = [
        term for term in high_risk_terms
        if term in claim_lower
    ]

    if matched_high_risk:
        score += 40
        risk_reasons.append(
            "The claim contains potentially high-risk medical instructions."
        )

    # --------------------------------------------------
    # 3. Diagnosis / treatment claims
    # --------------------------------------------------

    treatment_terms = [
        "cure",
        "cures",
        "treat",
        "treatment",
        "diagnose",
        "diagnosis",
        "prevent",
        "prevents",
        "eliminate",
        "eliminates"
    ]

    matched_treatment = [
        term for term in treatment_terms
        if term in claim_lower
    ]

    if matched_treatment:
        score += 15
        risk_reasons.append(
            "The claim makes a treatment, prevention, or diagnosis-related assertion."
        )

    # --------------------------------------------------
    # 4. Absolute / guaranteed language
    # --------------------------------------------------

    absolute_terms = [
        "always",
        "never",
        "completely",
        "guaranteed",
        "100%",
        "everyone",
        "no side effects",
        "perfectly safe"
    ]

    matched_absolute = [
        term for term in absolute_terms
        if term in claim_lower
    ]

    if matched_absolute:
        score += 10
        risk_reasons.append(
            "The claim uses absolute or overly certain language."
        )

    # --------------------------------------------------
    # 5. Safety flags from evidence retrieval
    # --------------------------------------------------

    if safety_flags:
        score += 10
        risk_reasons.append(
            "A MEDTRUST safety rule was triggered."
        )

    # --------------------------------------------------
    # 6. Cap score
    # --------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------
    # 7. Convert score into risk level
    # --------------------------------------------------

    if score >= 75:
        risk_level = "CRITICAL"

    elif score >= 50:
        risk_level = "HIGH"

    elif score >= 25:
        risk_level = "MODERATE"

    else:
        risk_level = "LOW"

    # --------------------------------------------------
    # 8. Human review decision
    # --------------------------------------------------

    human_review = risk_level in [
        "HIGH",
        "CRITICAL"
    ]

    if not risk_reasons:
        risk_reasons.append(
            "No major risk indicators were detected."
        )

    return {
        "risk_level": risk_level,
        "risk_score": score,
        "reason": " ".join(risk_reasons),
        "human_review": human_review,
        "matched_high_risk_terms": matched_high_risk,
        "matched_treatment_terms": matched_treatment,
        "matched_absolute_terms": matched_absolute
    }


if __name__ == "__main__":

    from evidence_retriever import retrieve_evidence
    from verifier import verify_claim

    test_claims = [

        "Drinking enough water can help maintain normal hydration.",

        "Vitamin C completely prevents the common cold.",

        "Can eating mangoes completely cure hypertension?",

        "You should stop taking your medication immediately."
    ]

    print("\nMEDTRUST AI — Risk Analysis Test")
    print("=" * 65)

    for number, claim in enumerate(test_claims, start=1):

        evidence = retrieve_evidence(claim)

        verification = verify_claim(
            claim,
            evidence
        )

        risk = analyze_risk(
            claim,
            verification
        )

        print(f"\nClaim {number}:")
        print(claim)

        print(
            f"\nVerification: "
            f"{verification['status']}"
        )

        print(
            f"Risk Level: "
            f"{risk['risk_level']}"
        )

        print(
            f"Risk Score: "
            f"{risk['risk_score']}/100"
        )

        print(
            f"Human Review: "
            f"{'YES' if risk['human_review'] else 'NO'}"
        )

        print(
            f"Reason: "
            f"{risk['reason']}"
        )

        print("-" * 65)