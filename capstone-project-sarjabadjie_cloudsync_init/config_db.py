"""
config_db.py

Simple SQLite layer for CloudSync Manager configuration.

This is NOT a full metadata implementation yet; it only stores the
latest sync configuration so that the GUI can load/save it.

Database file: cloudsync_metadata.db
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
import datetime

DB_PATH = Path("cloudsync_metadata.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the basic tables if they don't exist."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                local_folder TEXT NOT NULL,
                bucket TEXT NOT NULL,
                prefix TEXT,
                profile TEXT,
                region TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_config(cfg: Dict[str, Any]) -> None:
    """Insert a new configuration row."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sync_config (local_folder, bucket, prefix, profile, region, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                cfg.get("local_folder"),
                cfg.get("bucket"),
                cfg.get("prefix"),
                cfg.get("profile"),
                cfg.get("region"),
                datetime.datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_latest_config() -> Optional[Dict[str, Any]]:
    """Return the most recently-saved configuration, or None."""
    if not DB_PATH.exists():
        return None

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT local_folder, bucket, prefix, profile, region FROM sync_config ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "local_folder": row[0],
            "bucket": row[1],
            "prefix": row[2],
            "profile": row[3],
            "region": row[4],
        }
    finally:
        conn.close()
