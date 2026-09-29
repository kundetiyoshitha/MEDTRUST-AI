from flask import Blueprint, request, jsonify

from ai_engine.pipeline import analyze_response
from database.database import get_connection


analysis_bp = Blueprint(
    "analysis",
    __name__,
    url_prefix="/api"
)


# ============================================================
# SAVE COMPLETE ANALYSIS
# ============================================================

def save_analysis(result):
    """
    Save a complete MEDTRUST AI analysis into SQLite.

    Saves:
        - Overall analysis
        - Individual claims
        - Retrieved evidence
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # SAVE OVERALL ANALYSIS
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO analyses (
                original_response,
                safety_score,
                overall_status,
                total_claims,
                supported_claims,
                uncertain_claims,
                contradicted_claims,
                high_risk_claims,
                critical_claims
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.get("response", ""),
                result.get("safety_score", 0),
                result.get("overall_status", "UNKNOWN"),
                result.get("total_claims", 0),
                result.get("supported_claims", 0),
                result.get("uncertain_claims", 0),
                result.get("contradicted_claims", 0),
                result.get("high_risk_claims", 0),
                result.get("critical_claims", 0),
            )
        )

        analysis_id = cursor.lastrowid

        # ----------------------------------------------------
        # SAVE EACH CLAIM
        # ----------------------------------------------------

        for item in result.get("claims", []):

            verification = item.get(
                "verification",
                {}
            )

            risk = item.get(
                "risk",
                {}
            )

            mitigation = item.get(
                "mitigation",
                {}
            )

            cursor.execute(
                """
                INSERT INTO claims (
                    analysis_id,
                    claim_number,
                    claim_text,
                    verification_status,
                    verification_confidence,
                    verification_reason,
                    risk_level,
                    risk_score,
                    mitigation_action,
                    safe_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,

                    item.get(
                        "claim_number",
                        0
                    ),

                    item.get(
                        "claim",
                        ""
                    ),

                    verification.get(
                        "status",
                        "UNKNOWN"
                    ),

                    verification.get(
                        "confidence",
                        0
                    ),

                    verification.get(
                        "reason",
                        ""
                    ),

                    risk.get(
                        "risk_level",
                        "UNKNOWN"
                    ),

                    risk.get(
                        "risk_score",
                        0
                    ),

                    mitigation.get(
                        "action",
                        "NONE"
                    ),

                    mitigation.get(
                        "safe_status",
                        ""
                    ),
                )
            )

            claim_id = cursor.lastrowid

            # ------------------------------------------------
            # SAVE RETRIEVED EVIDENCE
            #
            # The working pipeline stores evidence in:
            # item["evidence"]
            # ------------------------------------------------

            evidence_list = item.get(
                "evidence",
                []
            )

            for evidence in evidence_list:

                matched_keywords = evidence.get(
                    "matched_keywords",
                    []
                )

                if isinstance(
                    matched_keywords,
                    list
                ):

                    matched_keywords = ", ".join(
                        str(word)
                        for word in matched_keywords
                    )

                else:

                    matched_keywords = str(
                        matched_keywords
                    )

                cursor.execute(
                    """
                    INSERT INTO evidence (
                        claim_id,
                        source_record_id,
                        topic,
                        evidence_text,
                        source,
                        source_type,
                        strength,
                        relevance_score,
                        matched_keywords
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        claim_id,

                        evidence.get(
                            "id"
                        ),

                        evidence.get(
                            "topic"
                        ),

                        evidence.get(
                            "evidence"
                        ),

                        evidence.get(
                            "source"
                        ),

                        evidence.get(
                            "source_type"
                        ),

                        evidence.get(
                            "strength"
                        ),

                        evidence.get(
                            "relevance_score",
                            0
                        ),

                        matched_keywords
                    )
                )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        connection.commit()

        return analysis_id

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ============================================================
# ANALYZE API
# ============================================================

@analysis_bp.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    # --------------------------------------------------------
    # READ REQUEST
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "error": "No data was provided."
        }), 400

    response = str(
        data.get(
            "response",
            ""
        )
    ).strip()

    if not response:

        return jsonify({
            "success": False,
            "error": (
                "Please provide an AI-generated "
                "healthcare response."
            )
        }), 400

    # --------------------------------------------------------
    # RUN MEDTRUST AI
    # --------------------------------------------------------

    try:

        result = analyze_response(
            response
        )

        # ----------------------------------------------------
        # HANDLE PIPELINE FAILURE
        # ----------------------------------------------------

        if not result.get(
            "success",
            True
        ):

            return jsonify({
                "success": False,
                "error": result.get(
                    "error",
                    result.get(
                        "recommendation",
                        "Analysis could not be completed."
                    )
                ),
                "result": result
            }), 400

        # ----------------------------------------------------
        # SAVE TO DATABASE
        # ----------------------------------------------------

        analysis_id = save_analysis(
            result
        )

        result["analysis_id"] = (
            analysis_id
        )

        # ----------------------------------------------------
        # RETURN RESULT TO FRONTEND
        # ----------------------------------------------------

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as error:

        print(
            "MEDTRUST Analysis Error:",
            error
        )

        return jsonify({
            "success": False,
            "error": (
                "MEDTRUST AI could not complete "
                "the analysis."
            ),
            "details": str(error)
        }), 500