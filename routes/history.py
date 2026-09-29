from flask import Blueprint, jsonify
from database.database import get_connection

history_bp = Blueprint(
    "history",
    __name__,
    url_prefix="/api"
)


@history_bp.route("/history", methods=["GET"])
def get_history():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                analysis_id,
                safety_score,
                overall_status,
                total_claims,
                supported_claims,
                uncertain_claims,
                contradicted_claims,
                high_risk_claims,
                critical_claims,
                created_at
            FROM analyses
            ORDER BY created_at DESC
            """
        ).fetchall()

        history = []

        for row in rows:
            history.append({
                "analysis_id": row["analysis_id"],
                "safety_score": row["safety_score"],
                "overall_status": row["overall_status"],
                "total_claims": row["total_claims"],
                "supported_claims": row["supported_claims"],
                "uncertain_claims": row["uncertain_claims"],
                "contradicted_claims": row["contradicted_claims"],
                "high_risk_claims": row["high_risk_claims"],
                "critical_claims": row["critical_claims"],
                "created_at": row["created_at"]
            })

        return jsonify({
            "success": True,
            "history": history
        })

    except Exception as error:
        print("MEDTRUST History Error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        connection.close()


@history_bp.route("/history/<int:analysis_id>", methods=["GET"])
def get_analysis_detail(analysis_id):
    connection = get_connection()

    try:
        # Get the main analysis
        analysis = connection.execute(
            """
            SELECT *
            FROM analyses
            WHERE analysis_id = ?
            """,
            (analysis_id,)
        ).fetchone()

        if not analysis:
            return jsonify({
                "success": False,
                "error": "Analysis not found"
            }), 404

        # Get all claims belonging to this analysis
        claims = connection.execute(
            """
            SELECT *
            FROM claims
            WHERE analysis_id = ?
            ORDER BY claim_number
            """,
            (analysis_id,)
        ).fetchall()

        claim_list = []

        for claim in claims:

            # Get evidence for this claim
            evidence_rows = connection.execute(
                """
                SELECT *
                FROM evidence
                WHERE claim_id = ?
                ORDER BY relevance_score DESC
                """,
                (claim["claim_id"],)
            ).fetchall()

            evidence_list = []

            for evidence in evidence_rows:
                evidence_list.append({
                    "evidence_id": evidence["evidence_id"],
                    "source_record_id": evidence["source_record_id"],
                    "topic": evidence["topic"],
                    "evidence_text": evidence["evidence_text"],
                    "source": evidence["source"],
                    "source_type": evidence["source_type"],
                    "strength": evidence["strength"],
                    "relevance_score": evidence["relevance_score"],
                    "matched_keywords": evidence["matched_keywords"]
                })

            claim_list.append({
                "claim_id": claim["claim_id"],
                "claim_number": claim["claim_number"],
                "claim_text": claim["claim_text"],
                "verification_status": claim["verification_status"],
                "verification_confidence": claim["verification_confidence"],
                "verification_reason": claim["verification_reason"],
                "risk_level": claim["risk_level"],
                "risk_score": claim["risk_score"],
                "mitigation_action": claim["mitigation_action"],
                "safe_status": claim["safe_status"],
                "evidence": evidence_list
            })

        return jsonify({
            "success": True,
            "analysis": {
                "analysis_id": analysis["analysis_id"],
                "original_response": analysis["original_response"],
                "safety_score": analysis["safety_score"],
                "overall_status": analysis["overall_status"],
                "total_claims": analysis["total_claims"],
                "supported_claims": analysis["supported_claims"],
                "uncertain_claims": analysis["uncertain_claims"],
                "contradicted_claims": analysis["contradicted_claims"],
                "high_risk_claims": analysis["high_risk_claims"],
                "critical_claims": analysis["critical_claims"],
                "created_at": analysis["created_at"]
            },
            "claims": claim_list
        })

    except Exception as error:
        print("MEDTRUST Analysis Detail Error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        connection.close()