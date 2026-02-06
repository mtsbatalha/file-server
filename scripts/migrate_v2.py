"""
Migration script to add error_message column to protocols table
"""
import sqlite3
import os

db_path = "/opt/file-server/backend/database.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

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
        print("Column added successfully.")
    else:
        print("error_message column already exists.")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
