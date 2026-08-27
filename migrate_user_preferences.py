"""
One-time migration: adds the new columns to the existing
user_preferences table in railpulse.db WITHOUT deleting any
existing rows (users, preferences, notifications all stay intact).

Run from your project root:  python migrate_user_preferences.py
Safe to re-run — skips any column that already exists.
"""

import sqlite3

DB_PATH = "railpulse.db"

NEW_COLUMNS = [
    ("notify_delay", "BOOLEAN NOT NULL DEFAULT 1"),
    ("notify_cancellation", "BOOLEAN NOT NULL DEFAULT 1"),
    ("notify_weather", "BOOLEAN NOT NULL DEFAULT 0"),
    ("is_active", "BOOLEAN NOT NULL DEFAULT 1"),
    ("created_at", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
    ("updated_at", "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(user_preferences)")
existing_columns = {row[1] for row in cur.fetchall()}

added, skipped = 0, 0

for col_name, col_def in NEW_COLUMNS:
    if col_name in existing_columns:
        print(f"skip  {col_name} (already exists)")
        skipped += 1
        continue
    cur.execute(f"ALTER TABLE user_preferences ADD COLUMN {col_name} {col_def}")
    print(f"added {col_name}")
    added += 1

conn.commit()
conn.close()

print(f"\nDone: {added} column(s) added, {skipped} already existed.")
