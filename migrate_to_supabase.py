"""
One-off data lift: copy the login accounts (users) from the local SQLite
(railpulse.db) up to Supabase Postgres so people can sign in. Reads the OLD
sqlite file directly and writes through the app's SQLAlchemy models (which now
point at Supabase via DATABASE_URL in your .env).

- Creates users + notifications tables in Supabase if missing.
- Copies users only. notifications starts EMPTY (the old rows were fake seed
  alerts; real ones will be generated once a live rail feed is wired up).
- Skips user_preferences (already in Supabase).
- Idempotent: users already present (by id) are skipped. Safe to re-run.

Run:  ./venv/bin/python migrate_to_supabase.py
"""

import sqlite3

from database import Base, SessionLocal, engine
from models import User

SQLITE_PATH = "railpulse.db"

# Ensure users + notifications exist in Supabase (skips pre-existing tables).
Base.metadata.create_all(bind=engine)

src = sqlite3.connect(SQLITE_PATH)
src.row_factory = sqlite3.Row
db = SessionLocal()

users_added = 0

for row in src.execute("SELECT * FROM users"):
    if db.get(User, row["id"]):
        continue
    db.add(User(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        email=row["email"],
        hashed_password=row["hashed_password"],
        purpose=row["purpose"],
        is_active=bool(row["is_active"]),
    ))
    users_added += 1

db.commit()
db.close()
src.close()

print(f"Done: {users_added} user(s) migrated to Supabase. notifications left empty.")

