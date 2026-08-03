import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# DATABASE_URL examples:
#   SQLite (default, zero setup):  sqlite:///./hospital.db
#   PostgreSQL (Task 5 in the guide): postgresql+psycopg2://user:password@host:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "hospitalpg26.postgres.database.azure.com")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
