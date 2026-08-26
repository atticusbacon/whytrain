from datetime import date, timedelta

import pytest

from app.models import AthleteProfile, ExperienceLevel, Goal, RaceDistance
from app import storage


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Point the storage module at a throwaway DB file per test."""
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")
    storage.init_db()
    yield


def test_upsert_and_get_profile():
    profile = AthleteProfile(
        name="Sam",
        experience_level=ExperienceLevel.ADVANCED,
        current_weekly_mileage=55,
    )
    profile_id = storage.upsert_profile(profile)
    assert profile_id is not None

    fetched = storage.get_latest_profile()
    assert fetched.name == "Sam"
    assert fetched.current_weekly_mileage == 55


def test_update_existing_profile():
    profile = AthleteProfile(
        name="Sam",
        experience_level=ExperienceLevel.ADVANCED,
        current_weekly_mileage=55,
    )
    profile_id = storage.upsert_profile(profile)

    updated = AthleteProfile(
        id=profile_id,
        name="Sam",
        experience_level=ExperienceLevel.ADVANCED,
        current_weekly_mileage=60,
    )
    storage.upsert_profile(updated)

    fetched = storage.get_latest_profile()
    assert fetched.current_weekly_mileage == 60


def test_upsert_and_get_goal():
    profile_id = storage.upsert_profile(
        AthleteProfile(
            name="Sam",
            experience_level=ExperienceLevel.INTERMEDIATE,
            current_weekly_mileage=30,
        )
    )
    goal = Goal(
        athlete_id=profile_id,
        race_distance=RaceDistance.MARATHON,
        target_date=date.today() + timedelta(weeks=20),
        target_time="3:45:00",
        notes="First marathon",
    )
    storage.upsert_goal(goal)

    fetched = storage.get_latest_goal(profile_id)
    assert fetched.race_distance == RaceDistance.MARATHON
    assert fetched.notes == "First marathon"
