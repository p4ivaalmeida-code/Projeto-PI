import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "empresas.sqlite3"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    is_new = (not DB_PATH.exists()) or os.path.getsize(DB_PATH) == 0
    if not is_new:
        return

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(schema_sql)