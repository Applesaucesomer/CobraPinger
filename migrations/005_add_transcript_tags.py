import sqlite3
import os

def migrate(db_path):
    print("Running migration 005: add tags column to transcript...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(current_dir, '005_add_transcript_tags.sql')
    with open(sql_file, 'r') as f:
        sql = f.read()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(sql)
        conn.commit()
    print("Migration 005 completed successfully")

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(os.path.dirname(current_dir), 'db.sqlite')
    migrate(db_path)
