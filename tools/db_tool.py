import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'candidates.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER,
            strengths TEXT,
            gaps TEXT,
            recommendation TEXT,
            profile_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def db_insert(name, score, strengths, gaps, recommendation, profile_url):
    """Inserts a new candidate record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO candidates (name, score, strengths, gaps, recommendation, profile_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, score, strengths, gaps, recommendation, profile_url))
    conn.commit()
    conn.close()
    return "Record inserted successfully."

def db_select(name):
    """Retrieves a specific candidate by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, score, strengths, gaps, recommendation, profile_url, created_at FROM candidates WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "name": row[0],
            "score": row[1],
            "strengths": row[2],
            "gaps": row[3],
            "recommendation": row[4],
            "profile_url": row[5],
            "created_at": row[6]
        }
    return None

def db_list():
    """Lists all candidates in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, score, strengths, gaps, recommendation, profile_url, created_at FROM candidates")
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row[0], "score": row[1], "strengths": row[2], "gaps": row[3], "recommendation": row[4], "profile_url": row[5], "created_at": row[6]} for row in rows]

def db_top(limit=3):
    """Fetches the top-scoring candidates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, score, strengths, gaps, recommendation, profile_url, created_at FROM candidates ORDER BY score DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row[0], "score": row[1], "strengths": row[2], "gaps": row[3], "recommendation": row[4], "profile_url": row[5], "created_at": row[6]} for row in rows]

def db_delete(name):
    """Deletes a candidate record by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return f"Record for {name} deleted."
