from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.models import AthleteProfile, ExperienceLevel, Goal, RaceDistance


def test_athlete_profile_valid():
    profile = AthleteProfile(
        name="  Jordan  ",
        experience_level=ExperienceLevel.INTERMEDIATE,
        current_weekly_mileage=40,
    )
    assert profile.name == "Jordan"  # whitespace stripped
    assert profile.preferred_unit.value == "mi"  # default


def test_athlete_profile_rejects_blank_name():
    with pytest.raises(ValidationError):
        AthleteProfile(
            name="   ",
            experience_level=ExperienceLevel.BEGINNER,
            current_weekly_mileage=10,
        )


def test_athlete_profile_rejects_negative_mileage():
    with pytest.raises(ValidationError):
        AthleteProfile(
            name="Jordan",
            experience_level=ExperienceLevel.BEGINNER,
            current_weekly_mileage=-5,
        )


def test_goal_valid():
    goal = Goal(
        athlete_id=1,
        race_distance=RaceDistance.MARATHON,
        target_date=date.today() + timedelta(weeks=16),
        target_time="3:30:00",
    )
    assert goal.target_time == "3:30:00"


def test_goal_rejects_past_date():
    with pytest.raises(ValidationError):
        Goal(
            athlete_id=1,
            race_distance=RaceDistance.FIVE_K,
            target_date=date.today() - timedelta(days=1),
        )


def test_goal_rejects_bad_time_format():
    with pytest.raises(ValidationError):
        Goal(
            athlete_id=1,
            race_distance=RaceDistance.HALF_MARATHON,
            target_date=date.today() + timedelta(weeks=8),
            target_time="not-a-time",
        )


def test_goal_allows_blank_time():
    goal = Goal(
        athlete_id=1,
        race_distance=RaceDistance.TEN_K,
        target_date=date.today() + timedelta(weeks=4),
        target_time="",
    )
    assert goal.target_time is None
