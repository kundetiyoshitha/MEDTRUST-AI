document.addEventListener("DOMContentLoaded", () => {

    const analyzeButton =
        document.getElementById("analyzeButton");

    const responseInput =
        document.getElementById("aiResponse");

    const resultsSection =
        document.getElementById("analysisResults");

    const overallStatus =
        document.getElementById("overallStatus");

    const safetyScore =
        document.getElementById("safetyScore");

    const totalClaims =
        document.getElementById("totalClaims");

    const supportedClaims =
        document.getElementById("supportedClaims");

    const attentionClaims =
        document.getElementById("attentionClaims");

    const claimsList =
        document.getElementById("claimsList");


    // =========================================================
    // SAFETY CHECK
    // =========================================================

    if (
        !analyzeButton ||
        !responseInput
    ) {

        console.error(
            "MEDTRUST Analyzer elements not found."
        );

        return;
    }


    // =========================================================
    // ANALYZE BUTTON
    // =========================================================

    analyzeButton.addEventListener(
        "click",
        async () => {

            const response =
                responseInput.value.trim();


            if (!response) {

                alert(
                    "Please enter an AI-generated healthcare response first."
                );

                return;
            }


            // Loading state
            analyzeButton.disabled = true;

            analyzeButton.innerHTML =
                "<span>⟳</span> Analyzing...";


            try {

                const apiResponse =
                    await fetch(
                        "/api/analyze",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                response:
                                    response
                            })
                        }
                    );


                let data;


                try {

                    data =
                        await apiResponse.json();

                } catch (error) {

                    throw new Error(
                        `Server returned an invalid response (HTTP ${apiResponse.status}).`
                    );

                }


                if (
                    !apiResponse.ok ||
                    !data.success
                ) {

                    throw new Error(
                        data.error ||
                        "Analysis failed."
                    );

                }


                // =================================================
                // SAVE LAST ANALYSIS
                // =================================================

                sessionStorage.setItem(
                    "medtrust_last_analysis",
                    JSON.stringify(
                        data.result
                    )
                );


                // Display results
                displayAnalysisResults(
                    data.result
                );


            } catch (error) {

                console.error(
                    "MEDTRUST Analyzer Error:",
                    error
                );


                alert(
                    "MEDTRUST could not analyze the response.\n\n" +
                    (
                        error.message ||
                        "Unknown error."
                    )
                );


            } finally {

                analyzeButton.disabled =
                    false;


                analyzeButton.innerHTML =
                    "<span>✦</span> Analyze with AI";

            }

        }
    );


    // =========================================================
    // DISPLAY COMPLETE RESULTS
    // =========================================================

    function displayAnalysisResults(
        result
    ) {

        if (!result) {
            return;
        }


        // Show result section
        if (resultsSection) {

            resultsSection.style.display =
                "block";

        }


        // =====================================================
        // OVERALL RESULT
        // =====================================================

        if (overallStatus) {

            overallStatus.textContent =
                result.overall_status ||
                "UNKNOWN";


            overallStatus.className =
                `status-badge ${getStatusClass(
                    result.overall_status
                )}`;

        }


        if (safetyScore) {

            safetyScore.textContent =
                result.safety_score ??
                "—";

        }


        if (totalClaims) {

            totalClaims.textContent =
                result.total_claims ??
                0;

        }


        if (supportedClaims) {

            supportedClaims.textContent =
                result.supported_claims ??
                0;

        }


        const attention =
            (
                result.uncertain_claims ||
                0
            ) +
            (
                result.contradicted_claims ||
                0
            );


        if (attentionClaims) {

            attentionClaims.textContent =
                attention;

        }


        // =====================================================
        // QUICK SUMMARY
        // =====================================================

        createResponseSummary(
            result
        );


        // =====================================================
        // HALLUCINATION FINGERPRINT
        // =====================================================

        createHallucinationFingerprint(
            result
        );


        // =====================================================
        // CLAIM LIST
        // =====================================================

        if (!claimsList) {
            return;
        }


        claimsList.innerHTML =
            "";


        const claims =
            Array.isArray(
                result.claims
            )
                ? result.claims
                : [];


        if (
            claims.length === 0
        ) {

            claimsList.innerHTML = `

                <div class="empty-state">

                    No meaningful claims were detected.

                </div>

            `;

            return;
        }


        // =====================================================
        // CREATE CLAIM CARDS
        // =====================================================

        claims.forEach(
            (
                item,
                index
            ) => {

                const verification =
                    item.verification ||
                    {};


                const risk =
                    item.risk ||
                    {};


                const mitigation =
                    item.mitigation ||
                    {};


                /*
                 * Current MEDTRUST pipeline stores
                 * retrieved evidence directly in:
                 *
                 * item.evidence
                 */

                const evidence =
                    Array.isArray(
                        item.evidence
                    )
                        ? item.evidence
                        : Array.isArray(
                            verification.medical_evidence
                        )
                            ? verification.medical_evidence
                            : [];


                const safetyFlags =
                    Array.isArray(
                        item.safety_flags
                    )
                        ? item.safety_flags
                        : Array.isArray(
                            verification.safety_flags
                        )
                            ? verification.safety_flags
                            : [];


                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "claim-result-card";


                const statusClass =
                    getStatusClass(
                        verification.status
                    );


                const riskClass =
                    getRiskClass(
                        risk.risk_level
                    );


                card.innerHTML = `

                    <div class="claim-card-top">

                        <div class="claim-number">

                            Claim ${escapeHtml(
                                String(
                                    item.claim_number ??
                                    index + 1
                                )
                            )}

                        </div>


                        <div class="claim-badges">

                            <span
                                class="claim-status ${statusClass}"
                            >

                                ${escapeHtml(
                                    verification.status ||
                                    "UNCERTAIN"
                                )}

                            </span>


                            <span
                                class="claim-risk ${riskClass}"
                            >

                                ${escapeHtml(
                                    risk.risk_level ||
                                    "UNKNOWN"
                                )}

                            </span>

                        </div>

                    </div>


                    <div class="claim-text">

                        ${escapeHtml(
                            item.claim ||
                            ""
                        )}

                    </div>


                    <div class="claim-details">


                        <div class="claim-detail">

                            <span
                                class="detail-label"
                            >
                                Confidence
                            </span>


                            <strong>
                                ${verification.confidence ?? 0}%
                            </strong>

                        </div>


                        <div class="claim-detail">

                            <span
                                class="detail-label"
                            >
                                Risk Score
                            </span>


                            <strong>
                                ${risk.risk_score ?? 0}/100
                            </strong>

                        </div>


                        <div class="claim-detail">

                            <span
                                class="detail-label"
                            >
                                Action
                            </span>


                            <strong>
                                ${escapeHtml(
                                    mitigation.action ||
                                    "REVIEW"
                                )}
                            </strong>

                        </div>


                    </div>


                    <div class="claim-reason">

                        <strong>
                            Why MEDTRUST flagged this
                        </strong>


                        <p>

                            ${escapeHtml(
                                verification.reason ||
                                "Additional review is required."
                            )}

                        </p>

                    </div>


                    ${createEvidenceSection(
                        evidence,
                        safetyFlags,
                        mitigation
                    )}

                `;


                claimsList.appendChild(
                    card
                );

            }
        );


        // =====================================================
        // SMOOTH SCROLL
        // =====================================================

        setTimeout(
            () => {

                if (resultsSection) {

                    resultsSection.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }

            },
            100
        );

    }


    // =========================================================
    // QUICK RESPONSE SUMMARY
    // =========================================================

    function createResponseSummary(
        result
    ) {

        const oldSummary =
            document.getElementById(
                "medtrustResponseSummary"
            );


        if (oldSummary) {
            oldSummary.remove();
        }


        const claims =
            Number(
                result.total_claims ||
                0
            );


        const attention =
            Number(
                result.uncertain_claims ||
                0
            ) +
            Number(
                result.contradicted_claims ||
                0
            );


        const evidenceFound =
            result.evidence_found ??
            countEvidence(result);


        const verdict =
            getBriefVerdict(
                result,
                attention
            );


        const summaryBox =
            document.createElement(
                "div"
            );


        summaryBox.id =
            "medtrustResponseSummary";


        summaryBox.className =
            "response-summary-card";


        summaryBox.innerHTML = `

            <div class="response-summary-header">

                <div>

                    <span class="summary-eyebrow">
                        QUICK RESULT
                    </span>


                    <h3>
                        MEDTRUST Safety Check
                    </h3>

                </div>


                <span
                    class="summary-status ${getStatusClass(
                        result.overall_status
                    )}"
                >

                    ${escapeHtml(
                        result.overall_status ||
                        "UNKNOWN"
                    )}

                </span>

            </div>


            <div class="response-summary-grid">


                <div class="summary-metric">

                    <span>
                        Safety Score
                    </span>


                    <strong>
                        ${result.safety_score ?? "—"}/100
                    </strong>

                </div>


                <div class="summary-metric">

                    <span>
                        Claims
                    </span>


                    <strong>
                        ${claims}
                    </strong>

                </div>


                <div class="summary-metric">

                    <span>
                        Supported
                    </span>


                    <strong>
                        ${result.supported_claims ?? 0}
                    </strong>

                </div>


                <div class="summary-metric">

                    <span>
                        Attention
                    </span>


                    <strong>
                        ${attention}
                    </strong>

                </div>


                <div class="summary-metric">

                    <span>
                        Evidence
                    </span>


                    <strong>
                        ${evidenceFound}
                    </strong>

                </div>


            </div>


            <div class="summary-recommendation">

                <div class="recommendation-icon">
                    ✦
                </div>


                <div>

                    <span>
                        Quick Summary
                    </span>


                    <p>
                        ${escapeHtml(
                            verdict
                        )}
                    </p>

                </div>

            </div>

        `;


        const claimsParent =
            claimsList
                ? claimsList.parentElement
                : null;


        if (
            claimsParent &&
            claimsList
        ) {

            claimsParent.insertBefore(
                summaryBox,
                claimsList
            );

        } else if (
            resultsSection
        ) {

            resultsSection.appendChild(
                summaryBox
            );

        }

    }


    // =========================================================
    // HALLUCINATION FINGERPRINT
    // =========================================================

    function createHallucinationFingerprint(
        result
    ) {

        const oldFingerprint =
            document.getElementById(
                "medtrustHallucinationFingerprint"
            );


        if (oldFingerprint) {
            oldFingerprint.remove();
        }


        const claims =
            Array.isArray(
                result.claims
            )
                ? result.claims
                : [];


        let contradictions =
            0;

        let insufficientEvidence =
            0;

        let absoluteWording =
            0;

        let highRiskContent =
            0;


        const absolutePattern =
            /\b(always|never|completely|guaranteed|guarantee|100%|totally|perfectly|none)\b/i;


        claims.forEach(
            item => {

                const verification =
                    item.verification ||
                    {};


                const risk =
                    item.risk ||
                    {};


                const status =
                    String(
                        verification.status ||
                        ""
                    ).toUpperCase();


                const riskLevel =
                    String(
                        risk.risk_level ||
                        ""
                    ).toUpperCase();


                const claimText =
                    String(
                        item.claim ||
                        ""
                    );


                if (
                    status ===
                    "CONTRADICTED"
                ) {

                    contradictions++;

                }


                if (
                    status ===
                    "UNCERTAIN"
                ) {

                    insufficientEvidence++;

                }


                if (
                    absolutePattern.test(
                        claimText
                    )
                ) {

                    absoluteWording++;

                }


                if (
                    riskLevel === "HIGH" ||
                    riskLevel === "CRITICAL"
                ) {

                    highRiskContent++;

                }

            }
        );


        const signals = [

            {
                label:
                    "Contradictions",

                value:
                    contradictions
            },


            {
                label:
                    "Insufficient Evidence",

                value:
                    insufficientEvidence
            },


            {
                label:
                    "Absolute Wording",

                value:
                    absoluteWording
            },


            {
                label:
                    "High-Risk Content",

                value:
                    highRiskContent
            }

        ];


        const maxValue =
            Math.max(
                ...signals.map(
                    signal =>
                        signal.value
                ),
                1
            );


        const reviewClaims =
            contradictions +
            insufficientEvidence;


        const fingerprint =
            document.createElement(
                "div"
            );


        fingerprint.id =
            "medtrustHallucinationFingerprint";


        fingerprint.className =
            "hallucination-fingerprint";


        fingerprint.innerHTML = `

            <div class="fingerprint-header">

                <div>

                    <span
                        class="fingerprint-eyebrow"
                    >
                        HALLUCINATION FINGERPRINT
                    </span>


                    <h4>
                        What caused the risk?
                    </h4>

                </div>


                <span
                    class="fingerprint-count"
                >

                    ${reviewClaims}

                    ${
                        reviewClaims === 1
                            ? "claim"
                            : "claims"
                    }

                    to review

                </span>

            </div>


            <div class="fingerprint-signals">

                ${
                    signals
                        .map(
                            signal => {

                                const width =
                                    signal.value === 0
                                        ? 0
                                        : Math.max(
                                            8,
                                            Math.round(
                                                (
                                                    signal.value /
                                                    maxValue
                                                ) *
                                                100
                                            )
                                        );


                                return `

                                    <div
                                        class="fingerprint-signal"
                                    >

                                        <div
                                            class="fingerprint-signal-top"
                                        >

                                            <span>
                                                ${escapeHtml(
                                                    signal.label
                                                )}
                                            </span>


                                            <strong>
                                                ${signal.value}
                                            </strong>

                                        </div>


                                        <div
                                            class="fingerprint-track"
                                        >

                                            <span
                                                class="fingerprint-fill"
                                                style="width:${width}%"
                                            ></span>

                                        </div>

                                    </div>

                                `;

                            }
                        )
                        .join("")
                }

            </div>

        `;


        const summary =
            document.getElementById(
                "medtrustResponseSummary"
            );


        if (
            summary &&
            summary.parentElement
        ) {

            summary.parentElement.insertBefore(
                fingerprint,
                summary.nextSibling
            );

        } else if (
            resultsSection
        ) {

            resultsSection.appendChild(
                fingerprint
            );

        }

    }


    // =========================================================
    // BRIEF VERDICT
    // =========================================================

    function getBriefVerdict(
        result,
        totalAttention
    ) {

        const contradicted =
            Number(
                result.contradicted_claims ||
                0
            );


        const uncertain =
            Number(
                result.uncertain_claims ||
                0
            );


        const total =
            Number(
                result.total_claims ||
                0
            );


        if (
            contradicted > 0 &&
            uncertain > 0
        ) {

            return (
                `${totalAttention} claims need attention: ` +
                `${contradicted} contradicted and ` +
                `${uncertain} need more evidence.`
            );

        }


        if (
            contradicted > 0
        ) {

            return (
                `${contradicted} ${
                    contradicted === 1
                        ? "claim conflicts"
                        : "claims conflict"
                } with trusted evidence.`
            );

        }


        if (
            uncertain > 0
        ) {

            return (
                `${uncertain} ${
                    uncertain === 1
                        ? "claim needs"
                        : "claims need"
                } additional verification.`
            );

        }


        if (
            total > 0 &&
            Number(
                result.supported_claims ||
                0
            ) === total
        ) {

            return (
                "All detected claims are supported by the available evidence."
            );

        }


        return (
            "Review the highlighted evidence before relying on this response."
        );

    }


    // =========================================================
    // EVIDENCE
    // =========================================================

    function createEvidenceSection(
        evidence,
        safetyFlags,
        mitigation
    ) {

        let html = "";


        // -----------------------------------------------------
        // MEDICAL EVIDENCE
        // -----------------------------------------------------

        if (
            evidence.length > 0
        ) {

            html += `

                <div class="evidence-box">

                    <div class="evidence-title">
                        ◈ Trusted Evidence
                    </div>

            `;


            evidence.forEach(
                item => {

                    const semanticScore =
                        formatScore(
                            item.semantic_score
                        );


                    const keywordScore =
                        formatScore(
                            item.keyword_score
                        );


                    const relevanceScore =
                        formatScore(
                            item.relevance_score ??
                            item.combined_score ??
                            item.score
                        );


                    html += `

                        <div
                            class="evidence-item"
                        >

                            <div
                                class="evidence-source-row"
                            >

                                <strong>

                                    ${escapeHtml(
                                        item.source ||
                                        "Medical Source"
                                    )}

                                </strong>


                                ${
                                    item.strength
                                        ? `

                                            <span
                                                class="evidence-strength"
                                            >

                                                ${escapeHtml(
                                                    item.strength
                                                )}

                                            </span>

                                        `
                                        : ""
                                }

                            </div>


                            ${
                                item.topic
                                    ? `

                                        <div
                                            class="evidence-topic"
                                        >

                                            ${escapeHtml(
                                                item.topic
                                            )}

                                        </div>

                                    `
                                    : ""
                            }


                            <p>

                                ${escapeHtml(
                                    item.evidence ||
                                    ""
                                )}

                            </p>


                            <div
                                class="evidence-metrics"
                            >

                                <span>

                                    Semantic

                                    <strong>
                                        ${semanticScore}
                                    </strong>

                                </span>


                                <span>

                                    Keyword

                                    <strong>
                                        ${keywordScore}
                                    </strong>

                                </span>


                                <span>

                                    Relevance

                                    <strong>
                                        ${relevanceScore}
                                    </strong>

                                </span>

                            </div>


                            ${
                                item.source_type
                                    ? `

                                        <div
                                            class="evidence-source-type"
                                        >

                                            Source type:

                                            ${escapeHtml(
                                                item.source_type
                                            )}

                                        </div>

                                    `
                                    : ""
                            }


                            ${
                                item.url
                                    ? `

                                        <div
                                            class="evidence-source-type"
                                        >

                                            Source:

                                            <a
                                                href="${escapeAttribute(
                                                    item.url
                                                )}"
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            >
                                                View source
                                            </a>

                                        </div>

                                    `
                                    : ""
                            }

                        </div>

                    `;

                }
            );


            html += `

                </div>

            `;

        }


        // -----------------------------------------------------
        // SAFETY FLAGS
        // -----------------------------------------------------

        if (
            safetyFlags.length > 0
        ) {

            html += `

                <div
                    class="safety-warning"
                >

                    <div
                        class="evidence-title"
                    >

                        ⚠ Safety Flag

                    </div>

            `;


            safetyFlags.forEach(
                flag => {

                    html += `

                        <div
                            class="safety-flag-item"
                        >

                            <strong>

                                ${escapeHtml(
                                    flag.topic ||
                                    "Safety Rule"
                                )}

                            </strong>


                            <p>

                                ${escapeHtml(
                                    flag.evidence ||
                                    ""
                                )}

                            </p>

                        </div>

                    `;

                }
            );


            html += `

                </div>

            `;

        }


        // -----------------------------------------------------
        // MITIGATION
        // -----------------------------------------------------

        if (
            mitigation &&
            mitigation.safe_status
        ) {

            html += `

                <div
                    class="mitigation-box"
                >

                    <div
                        class="mitigation-label"
                    >
                        MEDTRUST Action
                    </div>


                    <strong>

                        ${escapeHtml(
                            mitigation.safe_status
                        )}

                    </strong>


                    ${
                        mitigation.corrected_response
                            ? `

                                <p>

                                    ${escapeHtml(
                                        mitigation.corrected_response
                                    )}

                                </p>

                            `
                            : ""
                    }

                </div>

            `;

        }


        return html;

    }


    // =========================================================
    // COUNT EVIDENCE
    // =========================================================

    function countEvidence(
        result
    ) {

        if (
            !Array.isArray(
                result.claims
            )
        ) {

            return 0;

        }


        return result.claims.reduce(
            (
                total,
                item
            ) => {

                if (
                    Array.isArray(
                        item.evidence
                    )
                ) {

                    return (
                        total +
                        item.evidence.length
                    );

                }


                const verification =
                    item.verification ||
                    {};


                if (
                    Array.isArray(
                        verification.medical_evidence
                    )
                ) {

                    return (
                        total +
                        verification
                            .medical_evidence
                            .length
                    );

                }


                return total;

            },
            0
        );

    }


    // =========================================================
    // SCORE FORMAT
    // =========================================================

    function formatScore(
        value
    ) {

        if (
            value === undefined ||
            value === null ||
            value === ""
        ) {

            return "—";

        }


        const number =
            Number(value);


        if (
            Number.isNaN(
                number
            )
        ) {

            return "—";

        }


        return number.toFixed(2);

    }


    // =========================================================
    // STATUS CLASS
    // =========================================================

    function getStatusClass(
        status
    ) {

        const normalized =
            String(
                status || ""
            ).toUpperCase();


        if (
            normalized ===
            "SUPPORTED" ||

            normalized ===
            "LOW RISK" ||

            normalized ===
            "SAFE"
        ) {

            return "status-supported";

        }


        if (
            normalized ===
            "CONTRADICTED" ||

            normalized ===
            "HIGH RISK" ||

            normalized ===
            "CRITICAL"
        ) {

            return "status-contradicted";

        }


        return "status-uncertain";

    }


    // =========================================================
    // RISK CLASS
    // =========================================================

    function getRiskClass(
        level
    ) {

        const normalized =
            String(
                level || ""
            ).toUpperCase();


        if (
            normalized ===
            "CRITICAL"
        ) {

            return "risk-critical";

        }


        if (
            normalized ===
            "HIGH"
        ) {

            return "risk-high";

        }


        if (
            normalized ===
            "MODERATE"
        ) {

            return "risk-moderate";

        }


        return "risk-low";

    }


    // =========================================================
    // HTML ESCAPE
    // =========================================================

    function escapeHtml(
        text
    ) {

        if (
            text === undefined ||
            text === null
        ) {

            return "";

        }


        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            String(text);


        return div.innerHTML;

    }


    // =========================================================
    // ATTRIBUTE ESCAPE
    // =========================================================

    function escapeAttribute(
        value
    ) {

        return escapeHtml(
            value
        ).replace(
            /"/g,
            "&quot;"
        );

    }

});