def mitigate_claim(claim, verification_result, risk_result):
    """
    Decide what MEDTRUST should do after verification and
    risk analysis.

    Actions:
        ACCEPT
        WARN
        FLAG
        ESCALATE
    """

    status = verification_result.get(
        "status",
        "UNCERTAIN"
    )

    risk_level = risk_result.get(
        "risk_level",
        "LOW"
    )

    medical_evidence = verification_result.get(
        "medical_evidence",
        []
    )

    human_review = risk_result.get(
        "human_review",
        False
    )

    # --------------------------------------------------
    # CRITICAL / HIGH RISK
    # --------------------------------------------------

    if risk_level in ["CRITICAL", "HIGH"]:

        return {
            "action": "ESCALATE",
            "safe_status": "Human Review Required",
            "message": (
                "This claim may create significant health risk "
                "if it is incorrect. MEDTRUST recommends human "
                "expert review before relying on this information."
            ),
            "corrected_response": None,
            "evidence": medical_evidence
        }

    # --------------------------------------------------
    # CONTRADICTED CLAIM
    # --------------------------------------------------

    if status == "CONTRADICTED":

        correction = None

        if medical_evidence:
            correction = (
                "The original claim conflicts with the available "
                "medical evidence. The evidence should be reviewed "
                "before accepting the claim."
            )

        return {
            "action": "FLAG",
            "safe_status": "Potential Hallucination",
            "message": (
                "The claim conflicts with retrieved medical evidence."
            ),
            "corrected_response": correction,
            "evidence": medical_evidence
        }

    # --------------------------------------------------
    # UNCERTAIN CLAIM
    # --------------------------------------------------

    if status == "UNCERTAIN":

        return {
            "action": "WARN",
            "safe_status": "Insufficient Evidence",
            "message": (
                "MEDTRUST could not find enough reliable evidence "
                "to confidently verify this claim. Avoid treating "
                "the claim as established medical fact."
            ),
            "corrected_response": (
                "Evidence is currently insufficient to confidently "
                "support this claim."
            ),
            "evidence": medical_evidence
        }

    # --------------------------------------------------
    # SUPPORTED CLAIM
    # --------------------------------------------------

    if status == "SUPPORTED":

        return {
            "action": "ACCEPT",
            "safe_status": "Supported",
            "message": (
                "Relevant medical evidence was found and no "
                "major contradiction was detected."
            ),
            "corrected_response": claim,
            "evidence": medical_evidence
        }

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------

    return {
        "action": "WARN",
        "safe_status": "Needs Review",
        "message": (
            "MEDTRUST could not confidently determine "
            "the safety of this claim."
        ),
        "corrected_response": None,
        "evidence": medical_evidence
    }


if __name__ == "__main__":

    from evidence_retriever import retrieve_evidence
    from verifier import verify_claim
    from risk_analyzer import analyze_risk

    test_claims = [

        "Drinking enough water can help maintain normal hydration.",

        "Vitamin C completely prevents the common cold.",

        "Can eating mangoes completely cure hypertension?",

        "You should stop taking your medication immediately."
    ]

    print("\nMEDTRUST AI — Mitigation Test")
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

        mitigation = mitigate_claim(
            claim,
            verification,
            risk
        )

        print(f"\nClaim {number}:")
        print(claim)

        print(
            f"\nVerification: "
            f"{verification['status']}"
        )

        print(
            f"Risk: "
            f"{risk['risk_level']} "
            f"({risk['risk_score']}/100)"
        )

        print(
            f"Action: "
            f"{mitigation['action']}"
        )

        print(
            f"Safety Status: "
            f"{mitigation['safe_status']}"
        )

        print(
            f"Message: "
            f"{mitigation['message']}"
        )

        if mitigation["corrected_response"]:
            print(
                f"Safer Response: "
                f"{mitigation['corrected_response']}"
            )

        print("-" * 65)