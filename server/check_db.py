"""
Test PostgreSQL connection before init_db.

Run from project root:
  python -m server.check_db
"""
import os
import sys

from server.config import build_database_uri, get_db_driver, get_pg_connect_kwargs


def _warn_cyrillic_path() -> None:
    cwd = os.getcwd()
    try:
        cwd.encode("ascii")
    except UnicodeEncodeError:
        print("WARNING: Project path contains non-ASCII characters (e.g. Cyrillic).")
        print("  Path:", cwd)
        print("  Using pg8000 driver to avoid psycopg2/libpq encoding bugs on Windows.")
        print("  If problems continue, move project to C:\\Projects\\Diplom")
        print()


def _connect_pg8000(dbname: str):
    import pg8000.native

    kw = get_pg_connect_kwargs(dbname)
    return pg8000.native.Connection(
        user=kw["user"],
        password=kw["password"],
        host=kw["host"],
        port=kw["port"],
        database=kw["database"],
    )


def _connect_psycopg2(dbname: str):
    import psycopg2

    kw = get_pg_connect_kwargs(dbname)
    return psycopg2.connect(
        host=kw["host"],
        port=kw["port"],
        user=kw["user"],
        password=kw["password"],
        dbname=kw["database"],
    )


def connect(dbname: str):
    driver = get_db_driver()
    if driver == "pg8000":
        return _connect_pg8000(dbname)
    return _connect_psycopg2(dbname)


def ensure_database() -> None:
    _warn_cyrillic_path()
    target = os.getenv("PGDATABASE", "pollpoint")
    kw = get_pg_connect_kwargs(target)
    print(f"Driver: {get_db_driver()}")
    print(f"Checking PostgreSQL: {kw['host']}:{kw['port']} db={target}")

    try:
        conn = connect(target)
        if get_db_driver() == "pg8000":
            conn.run("SELECT 1")
            conn.close()
        else:
            conn.close()
        print("OK: connected to database", target)
        return
    except Exception as e:
        print("Cannot connect to database:", target)
        print("Reason:", repr(e))

    print("Trying to create database via 'postgres' ...")
    try:
        if get_db_driver() == "pg8000":
            conn = connect("postgres")
            rows = conn.run("SELECT 1 FROM pg_database WHERE datname = :name", name=target)
            if not rows:
                conn.run(f'CREATE DATABASE "{target}"')
                print("Created database:", target)
            else:
                print("Database already exists:", target)
            conn.close()
            conn2 = connect(target)
            conn2.run("SELECT 1")
            conn2.close()
        else:
            import psycopg2

            conn = connect("postgres")
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target,))
            if not cur.fetchone():
                cur.execute(f'CREATE DATABASE "{target}"')
                print("Created database:", target)
            else:
                print("Database already exists:", target)
            cur.close()
            conn.close()
            conn2 = connect(target)
            conn2.close()

        print("OK: connected after create")
    except Exception as e:
        pwd = os.getenv("PGPASSWORD", "postgres")
        safe_uri = build_database_uri().replace(pwd, "****")
        print("\nFAILED. Check:")
        print("  1) PostgreSQL service is running (services.msc)")
        print("  2) server\\.env -> PGPASSWORD = your postgres password")
        print("  3) Password uses ASCII letters/numbers only")
        print("  4) PGHOST=127.0.0.1")
        print("  5) In pgAdmin run: CREATE DATABASE pollpoint;")
        print("\nURI:", safe_uri)
        print("\nError:", repr(e))
        sys.exit(1)


if __name__ == "__main__":
    ensure_database()
