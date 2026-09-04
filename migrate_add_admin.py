"""
One-time migration: adds `is_admin` to the existing `users` table.
Safe to re-run — uses IF NOT EXISTS, so running it twice does nothing bad.
"""
from sqlalchemy import text
from database import engine

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE
    """))

print("Migration complete: users.is_admin added (or already existed).")
