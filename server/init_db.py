"""
Create tables via SQLAlchemy.

Run from project root:
  python -m server.init_db
"""
import sys

from server.app import create_app, db
from server.check_db import ensure_database
import server.models  # noqa: F401


def init_db():
    ensure_database()
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            print("Tables created (SQLAlchemy create_all).")
        except Exception as e:
            print("\ninit_db FAILED:", repr(e))
            print("Check server\\.env (PGPASSWORD, PGHOST=127.0.0.1)")
            sys.exit(1)


if __name__ == "__main__":
    init_db()
