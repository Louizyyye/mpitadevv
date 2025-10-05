"""
Multi-database SQLAlchemy handler with backwards-compatible single-engine exports.

- Exports `engine` and `SessionLocal` for legacy code that expects a single DB.
- Also exposes `engines` and `Sessions` for multi-db usage.
- Provides get_db (generator) for FastAPI Depends usage.
- Provides get_db_context() for manual 'with' usage.
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

# ---- Basic credentials / defaults (override via .env) ----
MYSQL_USER = os.getenv("MYSQL_USER", os.getenv("DB_USER", "root"))
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", os.getenv("DB_PASS", "password"))
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")

# Primary (default) database URL
DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/mpita_medical"
)

# Additional DBs (optional)
DATABASES: Dict[str, str] = {
    "main": DEFAULT_DATABASE_URL,
    "trading": os.getenv(
        "TRADING_DB_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/mpita_trading"
    ),
    "analytics": os.getenv(
        "ANALYTICS_DB_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/mpita_analytics"
    ),
}

# ---- Create engines and sessionmakers for each configured DB ----
engines: Dict[str, any] = {}
Sessions: Dict[str, sessionmaker] = {}

ENGINE_KW = dict(
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={"charset": "utf8mb4", "connect_timeout": 30},
)

for name, url in DATABASES.items():
    try:
        engines[name] = create_engine(url, **ENGINE_KW)
        Sessions[name] = sessionmaker(bind=engines[name], autocommit=False, autoflush=False)
        print(f"[INFO] Engine created for '{name}' -> {url}")
    except Exception as e:
        print(f"[ERROR] Failed to create engine for '{name}': {e}")

# ---- Backwards-compatible single-engine exports (default = "main") ----
engine = engines["main"]
SessionLocal = Sessions["main"]

# ---- Declarative Base ----
Base = declarative_base()

# ---- FastAPI dependency generator ----
def get_db(db_name: str = "main") -> Generator[Session, None, None]:
    """Yields a SQLAlchemy session for FastAPI dependency injection."""
    if db_name not in Sessions:
        raise ValueError(f"Unknown database '{db_name}'")

    db = Sessions[db_name]()
    try:
        yield db
    finally:
        db.close()

# ---- Context manager version ----
@contextmanager
def get_db_context(db_name: str = "main") -> Generator[Session, None, None]:
    """Context manager for direct usage (e.g. with get_db_context('analytics') as db:)."""
    if db_name not in Sessions:
        raise ValueError(f"Unknown database '{db_name}'")

    db = Sessions[db_name]()
    try:
        yield db
    finally:
        db.close()

# ---- Database setup utilities ----
def init_db(db_name: str = None):
    """
    Create all tables.
    If db_name is None, it initializes all configured databases.
    """
    if db_name:
        if db_name not in engines:
            raise ValueError(f"Unknown database '{db_name}'")
        Base.metadata.create_all(bind=engines[db_name])
        print(f"[INFO] Created tables in database: {db_name}")
    else:
        for name, eng in engines.items():
            Base.metadata.create_all(bind=eng)
            print(f"[INFO] Created tables in database: {name}")

def drop_db(db_name: str = None):
    """
    Drop all tables (use only for development/testing).
    """
    if db_name:
        if db_name not in engines:
            raise ValueError(f"Unknown database '{db_name}'")
        Base.metadata.drop_all(bind=engines[db_name])
        print(f"[WARNING] Dropped tables in database: {db_name}")
    else:
        for name, eng in engines.items():
            Base.metadata.drop_all(bind=eng)
            print(f"[WARNING] Dropped tables in database: {name}")

# ---- Test connection helper ----
def test_connection(db_name: str = "main") -> bool:
    """
    Simple ping test for DB connectivity.
    """
    if db_name not in engines:
        raise ValueError(f"Unknown database '{db_name}'")

    try:
        with engines[db_name].connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[SUCCESS] Connection OK to '{db_name}'")
        return True
    except Exception as exc:
        print(f"[ERROR] Connection failed for '{db_name}': {exc}")
        return False
