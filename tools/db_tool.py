import sqlite3
import os
import logging

# Configure basic logging for database operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'candidates.db')

def get_connection():
    """Initializes and returns a database connection with standard settings."""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=10) # 10s timeout for concurrent access
        conn.row_factory = sqlite3.Row # Access results by column name
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
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
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def db_insert(name, score, strengths, gaps, recommendation, profile_url):
    """Inserts or updates a candidate record."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Using INSERT OR REPLACE for production flexibility
        cursor.execute("""
            INSERT OR REPLACE INTO candidates (name, score, strengths, gaps, recommendation, profile_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, score, strengths, gaps, recommendation, profile_url))
        conn.commit()
        conn.close()
        logger.info(f"Successfully inserted record for: {name}")
        return "Record inserted/updated successfully."
    except Exception as e:
        logger.error(f"Insert failed for {name}: {e}")
        return f"Error: {str(e)}"

def db_select(name):
    """Retrieves a specific candidate by name."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    except Exception as e:
        logger.error(f"Select failed for {name}: {e}")
        return None

def db_list():
    """Lists all candidates in the database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"List failed: {e}")
        return []

def db_top(limit=3):
    """Fetches the top-scoring candidates."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates ORDER BY score DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Top fetch failed: {e}")
        return []

def db_delete(name):
    """Deletes a candidate record by name."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM candidates WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        logger.info(f"Deleted record for: {name}")
        return f"Record for {name} deleted."
    except Exception as e:
        logger.error(f"Delete failed for {name}: {e}")
        return f"Error: {str(e)}"
