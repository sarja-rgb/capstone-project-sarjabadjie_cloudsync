import sqlite3
from datetime import datetime, timezone
import spacy

DB_NAME = "cloudsync_metadata.db"

SAMPLE_TEXT = """
CloudSync Manager is a Python desktop application for cloud storage management.
The project uses AWS S3, SQLite, and a local metadata database to track files,
sync history, and future AI-generated text insights. This demo verifies that
spaCy can extract text metadata and save the result into SQLite for advisor review.
"""

def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_text_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT NOT NULL,
            created_utc TEXT NOT NULL,
            summary TEXT NOT NULL,
            keywords TEXT NOT NULL,
            entities TEXT NOT NULL
        )
    """)
    conn.commit()

def simple_summary(text, max_words=35):
    words = text.strip().split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def main():
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")

    print("Processing sample CloudSync text...")
    doc = nlp(SAMPLE_TEXT)

    entities = []
    for ent in doc.ents:
        entities.append(f"{ent.text} -> {ent.label_}")

    keywords = []
    for token in doc:
        if token.is_alpha and not token.is_stop and len(token.text) > 3:
            lemma = token.lemma_.lower()
            if lemma not in keywords:
                keywords.append(lemma)

    summary = simple_summary(SAMPLE_TEXT)
    created_utc = datetime.now(timezone.utc).isoformat()

    print("Saving AI text metadata to SQLite...")
    conn = sqlite3.connect(DB_NAME)
    create_table(conn)

    conn.execute("""
        INSERT INTO ai_text_metadata
        (source_name, created_utc, summary, keywords, entities)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "CloudSync spaCy demo text",
        created_utc,
        summary,
        ", ".join(keywords[:15]),
        "; ".join(entities)
    ))

    conn.commit()

    rows = conn.execute("""
        SELECT id, source_name, created_utc, summary, keywords, entities
        FROM ai_text_metadata
        ORDER BY id DESC
        LIMIT 3
    """).fetchall()

    conn.close()

    print("\nCloudSync Manager - AI Text Metadata Demo")
    print("=" * 55)
    print("Database:", DB_NAME)
    print("Table: ai_text_metadata")
    print("\nLatest saved rows:")
    for row in rows:
        print(row)

    print("\nPASS: spaCy text metadata was extracted and saved to SQLite.")

if __name__ == "__main__":
    main()
