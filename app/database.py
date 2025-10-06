"""
Multi-database SQLAlchemy handler for PostgreSQL (Render-ready).

- Uses psycopg3 (recommended by Render).
- Supports single or multi-database configurations.
- Exports:
    - engine, SessionLocal for legacy single DB code
    - engines, Sessions for multi-DB usage
    - get_db (FastAPI-compatible dependency)
    - get_db_context (manual context manager)
- Includes init_db, drop_db, test_connection utilities
"""

import os
from contextlib import contextmanager
from typing import Generator, Dict
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

# Load environment variables
load_dotenv()

# -------------------------------------------------------------------
# Environment Configuration
# -------------------------------------------------------------------
POSTGRES_USER = os.getenv("POSTGRES_USER", "mpita_admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ZdPfoG4xvhvaWQDTqY5YpNqEtTnJxIy7")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "dpg-d3goj6ili9vc73faa8a0-a")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mpita_medical")
# Render usually provides DATABASE_URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2+mysql+pymysql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Optional additional databases
DATABASES: Dict[str, str] = {
    "main": os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    ),
    "analytics": os.getenv(
        "ANALYTICS_DB_URL",
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/mpita_analytics"
    ),
    "trading": os.getenv(
        "TRADING_DB_URL",
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/mpita_trading"
    ),
}


# Optional: print to verify
if __name__ == "__main__":
    for key, url in DATABASES.items():
        print(f"{key} => {url}")

# -------------------------------------------------------------------
# SQLAlchemy Engine + Session Config
# -------------------------------------------------------------------
ENGINE_KWARGS = dict(
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"connect_timeout": 30},
    echo=False,  # Set True for debugging
)

engines: Dict[str, any] = {}
Sessions: Dict[str, sessionmaker] = {}

for name, url in DATABASES.items():
    try:
        engines[name] = create_engine(url, **ENGINE_KWARGS)
        Sessions[name] = sessionmaker(bind=engines[name], autocommit=False, autoflush=False)
        print(f"[INFO] ✅ Engine created for '{name}' -> {url}")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to create engine for '{name}': {e}")

# -------------------------------------------------------------------
# Backwards-compatible single-engine exports
# -------------------------------------------------------------------
engine = engines["main"]
SessionLocal = Sessions["main"]

# Base class for models
Base = declarative_base()

# -------------------------------------------------------------------
# FastAPI dependency (for dependency injection)
# -------------------------------------------------------------------
def get_db(db_name: str = "main") -> Generator[Session, None, None]:
    """Yields a database session for FastAPI or direct use."""
    if db_name not in Sessions:
        raise ValueError(f"Unknown database '{db_name}'")

    db = Sessions[db_name]()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# Context manager (for scripts, management commands, etc.)
# -------------------------------------------------------------------
@contextmanager
def get_db_context(db_name: str = "main") -> Generator[Session, None, None]:
    """Context manager for direct DB usage."""
    if db_name not in Sessions:
        raise ValueError(f"Unknown database '{db_name}'")

    db = Sessions[db_name]()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------
def init_db(db_name: str = None):
    """Create all tables in the specified DB or all DBs."""
    if db_name:
        if db_name not in engines:
            raise ValueError(f"Unknown database '{db_name}'")
        Base.metadata.create_all(bind=engines[db_name])
        print(f"[INFO] ✅ Tables created in '{db_name}'")
    else:
        for db_name, eng in engines.items():
            Base.metadata.create_all(bind=eng)
            print(f"[INFO] ✅ Tables created in '{name}'")

def drop_db(db_name: str = None):
    """Drop all tables (use for development only)."""
    if db_name:
        if db_name not in engines:
            raise ValueError(f"Unknown database '{db_name}'")
        Base.metadata.drop_all(bind=engines[db_name])
        print(f"[WARNING] ⚠️ Dropped all tables in '{db_name}'")
    else:
        for db_name, eng in engines.items():
            Base.metadata.drop_all(bind=eng)
            print(f"[WARNING] ⚠️ Dropped all tables in '{name}'")

def test_connection(db_name: str = "main") -> bool:
    """Test connection for a given database."""
    if db_name not in engines:
        raise ValueError(f"Unknown database '{db_name}'")

    try:
        with engines[db_name].connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[SUCCESS] ✅ Connection OK to '{db_name}'")
        return True
    except Exception as exc:
        print(f"[ERROR] ❌ Connection failed for '{db_name}': {exc}")
        return False
