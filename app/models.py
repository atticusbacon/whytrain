"""Data contracts shared across the UI, storage layer, and (later) the LLM
orchestrator. Keeping these as plain pydantic models means the Strava/Garmin/
Coros integrations in a later stage can populate an AthleteProfile the same
way the manual-entry form does today -- nothing downstream needs to change
shape.
"""
from __future__ import annotations

import re
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DistanceUnit(str, Enum):
    MILES = "mi"
    KILOMETERS = "km"


class DataSource(str, Enum):
    """Where this profile's history came from. Manual entry is all that's
    wired up today; the other values exist now so storage/UI code doesn't
    need to change shape when stage 3 adds real integrations.
    """
    MANUAL = "manual"
    STRAVA = "strava"
    GARMIN = "garmin"
    COROS = "coros"


class RaceDistance(str, Enum):
    FIVE_K = "5k"
    TEN_K = "10k"
    HALF_MARATHON = "half_marathon"
    MARATHON = "marathon"
    ULTRA = "ultra"
    OTHER = "other"


TIME_PATTERN = re.compile(r"^\d{1,2}:\d{2}:\d{2}$")  # H:MM:SS or HH:MM:SS


class AthleteProfile(BaseModel):
    id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    experience_level: ExperienceLevel
    current_weekly_mileage: float = Field(ge=0, le=300)
    preferred_unit: DistanceUnit = DistanceUnit.MILES
    data_source: DataSource = DataSource.MANUAL

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name cannot be blank")
        return v


class Goal(BaseModel):
    id: Optional[int] = None
    athlete_id: int
    race_distance: RaceDistance
    target_date: date
    target_time: Optional[str] = Field(
        default=None,
        description="Optional finish-time target, formatted H:MM:SS or HH:MM:SS",
    )
    notes: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("target_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not TIME_PATTERN.match(v):
            raise ValueError("target_time must be formatted H:MM:SS or HH:MM:SS")
        return v

    @field_validator("target_date")
    @classmethod
    def validate_future_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("target_date cannot be in the past")
        return v
