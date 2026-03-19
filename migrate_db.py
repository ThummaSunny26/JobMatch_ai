import sqlite3
import os

DB_PATH = os.path.join('data', 'candidates.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    if 'created_at' not in columns:
        print("Adding 'created_at' column...")
        try:
            # Add column without a complex DEFAULT to avoid sqlite3 errors in some versions/environments
            cursor.execute("ALTER TABLE candidates ADD COLUMN created_at DATETIME")
            # Update existing rows to have a timestamp
            cursor.execute("UPDATE candidates SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")
    else:
        print("'created_at' column already exists.")
    
    conn.close()

if __name__ == "__main__":
    migrate()
