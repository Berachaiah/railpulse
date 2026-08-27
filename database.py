import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Create a .env file with your Supabase "
        "connection string, e.g. DATABASE_URL=postgresql://postgres.<ref>:"
        "<password>@aws-0-<region>.pooler.supabase.com:6543/postgres?sslmode=require"
    )

# NullPool: don't hold connections open between requests. This is the right
# choice for Supabase's transaction pooler (Supavisor) and serverless (Vercel),
# where the pooler manages connection reuse for us.
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
