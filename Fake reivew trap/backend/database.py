"""
Database module for Fake Review Trap.
Manages SQLite storage for analyzed product reviews and historical queries.
"""

import os
import sqlite3
import json
from datetime import datetime

DEFAULT_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "reviews.db")


def get_db_connection(db_path=None):
    """Create and return a database connection with row factory configured."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """Initialize the SQLite database schema if not already present."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review TEXT NOT NULL,
                rating INTEGER,
                verdict TEXT NOT NULL,
                score INTEGER NOT NULL,
                reasons TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reviews_created_at ON reviews(created_at DESC)")
        conn.commit()


def save_review(review, rating, verdict, score, reasons, details=None, db_path=None):
    """
    Save an analyzed review to the database.
    
    Args:
        review (str): The review text.
        rating (int or None): Star rating (1-5) or None.
        verdict (str): 'Fake', 'Suspicious', or 'Genuine'.
        score (int): Risk score (0-100).
        reasons (list): List of flagged reasons.
        details (dict or None): Dictionary of lexical & heuristic metrics.
        db_path (str, optional): Custom DB path.
        
    Returns:
        int: The inserted record ID.
    """
    path = db_path or DEFAULT_DB_PATH
    reasons_json = json.dumps(reasons)
    details_json = json.dumps(details or {})

    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (review, rating, verdict, score, reasons, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            review,
            rating,
            verdict,
            int(score),
            reasons_json,
            details_json,
            datetime.utcnow().isoformat() + "Z"
        ))
        conn.commit()
        return cursor.lastrowid


def get_history(limit=20, db_path=None):
    """
    Retrieve the most recent analyzed reviews.
    
    Args:
        limit (int): Maximum number of reviews to return (default 20).
        db_path (str, optional): Custom DB path.
        
    Returns:
        list of dict: Historical review entries.
    """
    path = db_path or DEFAULT_DB_PATH
    init_db(path)
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, review, rating, verdict, score, reasons, details, created_at
            FROM reviews
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    history = []
    for row in rows:
        try:
            reasons_list = json.loads(row["reasons"]) if row["reasons"] else []
        except Exception:
            reasons_list = [row["reasons"]] if row["reasons"] else []

        try:
            details_dict = json.loads(row["details"]) if row["details"] else {}
        except Exception:
            details_dict = {}

        history.append({
            "id": row["id"],
            "review": row["review"],
            "rating": row["rating"],
            "verdict": row["verdict"],
            "score": row["score"],
            "reasons": reasons_list,
            "details": details_dict,
            "created_at": row["created_at"]
        })

    return history


def clear_history(db_path=None):
    """
    Clear all records from the reviews table in SQLite.
    
    Args:
        db_path (str, optional): Custom DB path.
        
    Returns:
        int: Number of deleted rows.
    """
    path = db_path or DEFAULT_DB_PATH
    init_db(path)
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        cursor.execute("DELETE FROM reviews")
        cursor.execute("VACUUM")
        conn.commit()
        return count

