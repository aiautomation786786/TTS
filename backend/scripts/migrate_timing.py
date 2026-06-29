import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "db", "voxforge.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if generation_time_seconds exists in generations
    cursor.execute("PRAGMA table_info(generations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'generation_time_seconds' not in columns:
        print("Adding generation_time_seconds to generations table...")
        cursor.execute("ALTER TABLE generations ADD COLUMN generation_time_seconds FLOAT")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
