import os
import sqlite3
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "database", "face_security.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            distance REAL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_person(person_id, name):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO people(id, name, created_at) VALUES (?, ?, ?)",
        (person_id, name, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()


def get_people():
    conn = get_connection()
    rows = conn.execute("SELECT id, name FROM people ORDER BY id").fetchall()
    conn.close()
    return rows


def mark_attendance(person_id, name):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    conn = get_connection()
    exists = conn.execute(
        "SELECT 1 FROM attendance WHERE person_id=? AND date=?",
        (person_id, date)
    ).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO attendance(person_id,name,date,time) VALUES(?,?,?,?)",
            (person_id, name, date, time)
        )
        conn.commit()
        marked = True
    else:
        marked = False
    conn.close()
    return marked


def log_access(name, status, distance=None):
    now = datetime.now()
    conn = get_connection()
    conn.execute(
        "INSERT INTO access_logs(name,status,distance,date,time) VALUES(?,?,?,?,?,?)",
        (name, status, None if distance is None else float(distance),
         now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_today_attendance():
    date = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    rows = conn.execute(
        "SELECT name, date, time FROM attendance WHERE date=? ORDER BY time",
        (date,)
    ).fetchall()
    conn.close()
    return rows


def get_recent_logs(limit=20):
    conn = get_connection()
    rows = conn.execute(
        "SELECT name,status,distance,date,time FROM access_logs ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows
