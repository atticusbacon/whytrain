"""Plain sqlite3 persistence -- no ORM. The MVP is single-user (one runner,
one machine), so we don't need connection pooling or migrations yet; when
this grows multi-user, swap this module out without touching models.py or
the UI.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from app.models import AthleteProfile, Goal

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "running_widget.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS athlete_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    experience_level TEXT NOT NULL,
    current_weekly_mileage REAL NOT NULL,
    preferred_unit TEXT NOT NULL,
    data_source TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    athlete_id INTEGER NOT NULL REFERENCES athlete_profiles(id),
    race_distance TEXT NOT NULL,
    target_date TEXT NOT NULL,
    target_time TEXT,
    notes TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def upsert_profile(profile: AthleteProfile) -> int:
    """Insert a new profile, or update in place if profile.id is set.
    Returns the profile's id.
    """
    with get_connection() as conn:
        if profile.id is None:
            cur = conn.execute(
                """
                INSERT INTO athlete_profiles
                    (name, experience_level, current_weekly_mileage, preferred_unit, data_source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    profile.name,
                    profile.experience_level.value,
                    profile.current_weekly_mileage,
                    profile.preferred_unit.value,
                    profile.data_source.value,
                ),
            )
            return cur.lastrowid
        else:
            conn.execute(
                """
                UPDATE athlete_profiles
                SET name = ?, experience_level = ?, current_weekly_mileage = ?,
                    preferred_unit = ?, data_source = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    profile.name,
                    profile.experience_level.value,
                    profile.current_weekly_mileage,
                    profile.preferred_unit.value,
                    profile.data_source.value,
                    profile.id,
                ),
            )
            return profile.id


def get_latest_profile() -> Optional[AthleteProfile]:
    """MVP is single-user, so 'latest' is effectively 'the' profile."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM athlete_profiles ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return AthleteProfile(
            id=row["id"],
            name=row["name"],
            experience_level=row["experience_level"],
            current_weekly_mileage=row["current_weekly_mileage"],
            preferred_unit=row["preferred_unit"],
            data_source=row["data_source"],
        )


def upsert_goal(goal: Goal) -> int:
    with get_connection() as conn:
        if goal.id is None:
            cur = conn.execute(
                """
                INSERT INTO goals (athlete_id, race_distance, target_date, target_time, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    goal.athlete_id,
                    goal.race_distance.value,
                    goal.target_date.isoformat(),
                    goal.target_time,
                    goal.notes,
                ),
            )
            return cur.lastrowid
        else:
            conn.execute(
                """
                UPDATE goals
                SET race_distance = ?, target_date = ?, target_time = ?, notes = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    goal.race_distance.value,
                    goal.target_date.isoformat(),
                    goal.target_time,
                    goal.notes,
                    goal.id,
                ),
            )
            return goal.id


def get_latest_goal(athlete_id: int) -> Optional[Goal]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM goals WHERE athlete_id = ?
            ORDER BY updated_at DESC LIMIT 1
            """,
            (athlete_id,),
        ).fetchone()
        if row is None:
            return None
        return Goal(
            id=row["id"],
            athlete_id=row["athlete_id"],
            race_distance=row["race_distance"],
            target_date=row["target_date"],
            target_time=row["target_time"],
            notes=row["notes"],
        )
