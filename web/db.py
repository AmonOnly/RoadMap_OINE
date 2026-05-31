from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class UserSettings:
    user_id: int
    name: str
    hours_per_day: float
    days_planned: int
    goal: str
    language: str


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
  user_id INTEGER PRIMARY KEY,
  hours_per_day REAL NOT NULL,
  days_planned INTEGER NOT NULL,
  goal TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'pt',
  updated_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS progress (
  user_id INTEGER NOT NULL,
  day TEXT NOT NULL,
  completed INTEGER NOT NULL DEFAULT 0,
  xp INTEGER NOT NULL DEFAULT 0,
  streak INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, day),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS proficiency (
  user_id INTEGER NOT NULL,
  topic TEXT NOT NULL,
  score REAL NOT NULL DEFAULT 0.5,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (user_id, topic),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
  user_id INTEGER NOT NULL,
  day TEXT NOT NULL,
  correct INTEGER NOT NULL,
  total INTEGER NOT NULL,
  topic TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users(id)
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    conn = connect(db_path)
    try:
        conn.executescript(SCHEMA)
        columns = conn.execute("PRAGMA table_info(settings)").fetchall()
        names = {row["name"] for row in columns}
        if "language" not in names:
            conn.execute("ALTER TABLE settings ADD COLUMN language TEXT NOT NULL DEFAULT 'pt'")
        conn.commit()
    finally:
        conn.close()


def get_or_create_default_user(db_path: Path, name: str = "Aluno") -> int:
    conn = connect(db_path)
    try:
        row = conn.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
        if row:
            return int(row["id"])

        conn.execute(
            "INSERT INTO users (name, created_at) VALUES (?, date('now'))",
            (name,),
        )
        conn.commit()
        row = conn.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
        return int(row["id"])
    finally:
        conn.close()


def upsert_settings(
    db_path: Path,
    user_id: int,
    hours: float,
    days: int,
    goal: str,
    language: str,
) -> None:
    conn = connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO settings (user_id, hours_per_day, days_planned, goal, language, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                hours_per_day=excluded.hours_per_day,
                days_planned=excluded.days_planned,
                goal=excluded.goal,
                language=excluded.language,
                updated_at=datetime('now')
            """,
            (user_id, hours, days, goal, language),
        )
        conn.commit()
    finally:
        conn.close()


def load_settings(db_path: Path, user_id: int) -> UserSettings | None:
    conn = connect(db_path)
    try:
        row = conn.execute(
            "SELECT users.name, settings.hours_per_day, settings.days_planned, settings.goal, "
            "settings.language FROM settings JOIN users ON users.id=settings.user_id WHERE user_id=?",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        return UserSettings(
            user_id=user_id,
            name=row["name"],
            hours_per_day=float(row["hours_per_day"]),
            days_planned=int(row["days_planned"]),
            goal=row["goal"],
            language=row["language"],
        )
    finally:
        conn.close()


def update_name(db_path: Path, user_id: int, name: str) -> None:
    conn = connect(db_path)
    try:
        conn.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
        conn.commit()
    finally:
        conn.close()


def mark_day_complete(db_path: Path, user_id: int, day: date, xp_gain: int) -> tuple[int, int]:
    conn = connect(db_path)
    day_str = day.isoformat()
    try:
        prev = conn.execute(
            "SELECT completed, xp, streak FROM progress WHERE user_id=? AND day=?",
            (user_id, day_str),
        ).fetchone()
        if prev and prev["completed"]:
            return int(prev["xp"]), int(prev["streak"])

        previous_day = day.fromordinal(day.toordinal() - 1).isoformat()
        streak_row = conn.execute(
            "SELECT streak FROM progress WHERE user_id=? AND day=? AND completed=1",
            (user_id, previous_day),
        ).fetchone()
        streak = int(streak_row["streak"]) + 1 if streak_row else 1

        conn.execute(
            """
            INSERT INTO progress (user_id, day, completed, xp, streak)
            VALUES (?, ?, 1, ?, ?)
            ON CONFLICT(user_id, day) DO UPDATE SET
                completed=1,
                xp=excluded.xp,
                streak=excluded.streak
            """,
            (user_id, day_str, xp_gain, streak),
        )
        conn.commit()
        return xp_gain, streak
    finally:
        conn.close()


def load_progress_summary(db_path: Path, user_id: int, days: Iterable[str]) -> dict:
    conn = connect(db_path)
    try:
        placeholders = ",".join(["?"] * len(list(days)))
        rows = conn.execute(
            f"SELECT day, completed, xp, streak FROM progress WHERE user_id=? AND day IN ({placeholders})",
            (user_id, *list(days)),
        ).fetchall()
        result = {row["day"]: row for row in rows}
        return result
    finally:
        conn.close()


def add_quiz_attempt(
    db_path: Path,
    user_id: int,
    day: date,
    correct: int,
    total: int,
    topic: str,
) -> None:
    conn = connect(db_path)
    try:
        conn.execute(
            "INSERT INTO quiz_attempts (user_id, day, correct, total, topic, created_at) "
            "VALUES (?, ?, ?, ?, ?, datetime('now'))",
            (user_id, day.isoformat(), correct, total, topic),
        )
        conn.commit()
    finally:
        conn.close()


def update_proficiency(db_path: Path, user_id: int, topic: str, score: float) -> None:
    conn = connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO proficiency (user_id, topic, score, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(user_id, topic) DO UPDATE SET
                score=excluded.score,
                updated_at=datetime('now')
            """,
            (user_id, topic, score),
        )
        conn.commit()
    finally:
        conn.close()


def get_proficiency(db_path: Path, user_id: int, topic: str) -> float:
    conn = connect(db_path)
    try:
        row = conn.execute(
            "SELECT score FROM proficiency WHERE user_id=? AND topic=?",
            (user_id, topic),
        ).fetchone()
        if row:
            return float(row["score"])
        return 0.5
    finally:
        conn.close()


def get_stats(db_path: Path, user_id: int) -> dict:
    conn = connect(db_path)
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(xp), 0) as xp, COALESCE(MAX(streak), 0) as streak "
            "FROM progress WHERE user_id=? AND completed=1",
            (user_id,),
        ).fetchone()
        return {"xp": int(row["xp"]), "streak": int(row["streak"])}
    finally:
        conn.close()
