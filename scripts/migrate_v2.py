"""
Migration script to add error_message column to protocols table
Auto-detects database location from environment or common paths
"""
import sqlite3
import os
import sys

def find_database():
    """Find the database file in common locations"""
    possible_paths = [
        # From environment variable (if set)
        os.getenv("DATABASE_URL", "").replace("sqlite:///", "").replace("./", "/opt/file-server/"),
        # Common locations
        "/opt/file-server/fileserver.db",
        "/opt/file-server/backend/fileserver.db",
        "/opt/file-server/backend/database.db",
        "./fileserver.db",
        "./backend/fileserver.db",
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    return None

def run_migration():
    db_path = find_database()
    
    if not db_path:
        print("ERROR: Database not found in any of the expected locations.")
        print("Please set DATABASE_URL environment variable or specify the path manually.")
        sys.exit(1)
    
    print(f"Found database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(protocols)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "error_message" not in columns:
            print("Adding error_message column to protocols table...")
            cursor.execute("ALTER TABLE protocols ADD COLUMN error_message TEXT")
            conn.commit()
            print("✅ Column added successfully.")
        else:
            print("✅ error_message column already exists.")
    
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
