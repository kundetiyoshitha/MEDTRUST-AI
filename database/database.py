import sqlite3
from pathlib import Path


# ============================================================
# MEDTRUST AI DATABASE
# ============================================================

DATABASE_PATH = (
    Path(__file__).resolve().parent / "medtrust.db"
)


def get_connection():
    """
    Create and return a connection to the MEDTRUST SQLite database.

    SQLite is used because it is lightweight, requires no separate
    database server, and is suitable for our prototype.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign-key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """
    Create all MEDTRUST AI database tables if they do not exist.
    """

    connection = get_connection()

    cursor = connection.cursor()


    # ========================================================
    # 1. USERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            user_id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT,

            role TEXT NOT NULL DEFAULT 'user',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ========================================================
    # 2. ANALYSES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (

            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            original_response TEXT NOT NULL,

            safety_score INTEGER,

            overall_status TEXT,

            total_claims INTEGER DEFAULT 0,

            supported_claims INTEGER DEFAULT 0,

            uncertain_claims INTEGER DEFAULT 0,

            contradicted_claims INTEGER DEFAULT 0,

            high_risk_claims INTEGER DEFAULT 0,

            critical_claims INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE SET NULL
        )
    """)


    # ========================================================
    # 3. CLAIMS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS claims (

            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,

            analysis_id INTEGER NOT NULL,

            claim_number INTEGER NOT NULL,

            claim_text TEXT NOT NULL,

            verification_status TEXT,

            verification_confidence INTEGER,

            verification_reason TEXT,

            risk_level TEXT,

            risk_score INTEGER,

            mitigation_action TEXT,

            safe_status TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (analysis_id)
                REFERENCES analyses(analysis_id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # 4. EVIDENCE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (

            evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,

            claim_id INTEGER NOT NULL,

            source_record_id TEXT,

            topic TEXT,

            evidence_text TEXT,

            source TEXT,

            source_type TEXT,

            strength TEXT,

            relevance_score REAL,

            matched_keywords TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (claim_id)
                REFERENCES claims(claim_id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # 5. FEEDBACK
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (

            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,

            claim_id INTEGER,

            user_id INTEGER,

            feedback_type TEXT,

            comment TEXT,

            suggested_correction TEXT,

            validation_status TEXT DEFAULT 'PENDING',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (claim_id)
                REFERENCES claims(claim_id)
                ON DELETE SET NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE SET NULL
        )
    """)


    # ========================================================
    # 6. VALIDATED CORRECTIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validated_corrections (

            correction_id INTEGER PRIMARY KEY AUTOINCREMENT,

            feedback_id INTEGER,

            claim_id INTEGER,

            correction_text TEXT NOT NULL,

            verified_source TEXT,

            reviewed_by INTEGER,

            validation_status TEXT DEFAULT 'VALIDATED',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (feedback_id)
                REFERENCES feedback(feedback_id)
                ON DELETE SET NULL,

            FOREIGN KEY (claim_id)
                REFERENCES claims(claim_id)
                ON DELETE SET NULL,

            FOREIGN KEY (reviewed_by)
                REFERENCES users(user_id)
                ON DELETE SET NULL
        )
    """)


    # ========================================================
    # 7. KNOWLEDGE BASE
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (

            knowledge_id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic TEXT NOT NULL,

            evidence_text TEXT NOT NULL,

            source TEXT,

            source_type TEXT,

            strength TEXT,

            origin TEXT DEFAULT 'validated_feedback',

            correction_id INTEGER,

            active INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (correction_id)
                REFERENCES validated_corrections(correction_id)
                ON DELETE SET NULL
        )
    """)


    connection.commit()

    connection.close()


if __name__ == "__main__":

    init_db()

    print()
    print("=" * 60)
    print("MEDTRUST AI DATABASE")
    print("=" * 60)
    print()
    print("Database initialized successfully.")
    print(f"Location: {DATABASE_PATH}")
    print()
    print("Tables created:")
    print("1. users")
    print("2. analyses")
    print("3. claims")
    print("4. evidence")
    print("5. feedback")
    print("6. validated_corrections")
    print("7. knowledge_base")
    print()
    print("=" * 60)