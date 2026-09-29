"""
MEDTRUST AI database model documentation.

The actual database structure is created in database.py
using SQLite.

This file keeps the purpose of each table clearly documented
so the project is easier to understand and maintain.
"""


TABLES = {

    "users": {
        "purpose": "Stores application users and their roles."
    },

    "analyses": {
        "purpose": (
            "Stores every healthcare AI response analyzed "
            "by MEDTRUST."
        )
    },

    "claims": {
        "purpose": (
            "Stores individual claims extracted from an "
            "AI-generated response."
        )
    },

    "evidence": {
        "purpose": (
            "Stores evidence retrieved for each individual claim."
        )
    },

    "feedback": {
        "purpose": (
            "Stores user feedback and suggested corrections. "
            "Feedback is not automatically trusted."
        )
    },

    "validated_corrections": {
        "purpose": (
            "Stores corrections that have been reviewed and "
            "validated by an authorized reviewer."
        )
    },

    "knowledge_base": {
        "purpose": (
            "Stores trusted knowledge that can be used for "
            "future evidence-guided verification."
        )
    }
}


def describe_database():

    print("\nMEDTRUST AI DATABASE STRUCTURE")
    print("=" * 60)

    for table, details in TABLES.items():

        print(f"\n{table.upper()}")
        print("-" * len(table))
        print(details["purpose"])


if __name__ == "__main__":
    describe_database()