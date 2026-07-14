"""
database.py
-----------
Sets up the SQLAlchemy engine, session factory, and declarative Base.

The DATABASE_URL is read from the .env file. This project is written so the
SAME code works with SQLite (zero setup, great for a first run), PostgreSQL,
or MySQL. You only change one line in .env to switch.

Examples of DATABASE_URL:
  SQLite     -> sqlite:///./hcp_crm.db
  PostgreSQL -> postgresql+psycopg2://user:password@localhost:5432/hcp_crm
  MySQL      -> mysql+pymysql://user:password@localhost:3306/hcp_crm
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcp_crm.db")

# SQLite needs a special flag because FastAPI uses multiple threads.
# Other databases (Postgres/MySQL) do not need it.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
