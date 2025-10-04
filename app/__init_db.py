# create_and_init_db.py
import sys
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ----- CONFIG: change if needed -----
DB_USER = "root"
DB_PASSWORD = "cassanovaFry1!"   # your new password
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "mpita_medical"
# ------------------------------------

# URL-encode password safely (handles special chars)
pwd_quoted = quote_plus(DB_PASSWORD)

SERVER_URL = f"mysql+pymysql://{DB_USER}:{pwd_quoted}@{DB_HOST}:{DB_PORT}/"
DB_URL = f"mysql+pymysql://{DB_USER}:{pwd_quoted}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

ENGINE_KW = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "connect_args": {"charset": "utf8mb4", "connect_timeout": 30},
}

def main():
    try:
        # 1) Connect to server (no DB) and create the database if missing
        engine_server = create_engine(SERVER_URL, echo=False, **ENGINE_KW)
        with engine_server.connect() as conn:
            # MySQL requires CREATE DATABASE statement via text()
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            print(f"[OK] Ensured database `{DB_NAME}` exists.")
        engine_server.dispose()

        # 2) Create engine bound to the newly created DB
        engine = create_engine(DB_URL, echo=False, **ENGINE_KW)

        # 3) Patch your app.database to use this engine (so init_db works)
        import importlib
        try:
            dbmod = importlib.import_module("app.database")
        except Exception as e:
            print("[ERROR] Could not import app.database:", e)
            sys.exit(1)

        # overwrite engine and SessionLocal in app.database so its init_db uses the DB we just created
        dbmod.engine = engine
        dbmod.SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        print("[OK] Patched app.database.engine and SessionLocal.")

        # 4) Import models to register them against Base (app.models should import Base from app.database)
        try:
            importlib.import_module("app.models")
        except Exception as e:
            print("[ERROR] Could not import app.models:", e)
            # continue anyway; init_db may still work if models import Base properly
        # 5) Initialize tables using app.database.init_db()
        try:
            dbmod.init_db()
            print("[OK] Tables created successfully in", DB_NAME)
        except Exception as e:
            print("[ERROR] init_db() failed:", e)
            raise

    except Exception as exc:
        print("[FATAL] Script failed:", exc)
        raise

if __name__ == "__main__":
    main()
