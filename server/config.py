import os
import sys
from typing import Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_ENV_PATH, encoding="utf-8")
load_dotenv(encoding="utf-8")


def _pg_settings() -> dict:
    pwd = os.getenv("PGPASSWORD")
    if pwd is None:
        pwd = "postgres"
    return {
        "host": os.getenv("PGHOST", "127.0.0.1"),
        "port": int(os.getenv("PGPORT", "5432")),
        "user": os.getenv("PGUSER", "postgres"),
        "password": pwd,
        "database": os.getenv("PGDATABASE", "pollpoint"),
    }


def get_db_driver() -> str:
    """
    pg8000 = pure Python, works on Windows with Cyrillic paths.
    psycopg2 = default libpq driver (can fail on Windows + Cyrillic folder names).
    """
    driver = os.getenv("DB_DRIVER", "").strip().lower()
    if driver in ("pg8000", "psycopg2"):
        return driver
    if sys.platform == "win32":
        return "pg8000"
    return "psycopg2"


def build_database_uri() -> str:
    s = _pg_settings()
    driver = get_db_driver()
    scheme = f"postgresql+{driver}"
    return (
        f"{scheme}://{quote_plus(s['user'])}:{quote_plus(s['password'])}"
        f"@{s['host']}:{s['port']}/{quote_plus(s['database'])}"
    )


def get_pg_connect_kwargs(dbname: Optional[str] = None) -> dict:
    s = _pg_settings()
    return {
        "host": s["host"],
        "port": s["port"],
        "user": s["user"],
        "password": s["password"],
        "database": dbname if dbname is not None else s["database"],
    }
