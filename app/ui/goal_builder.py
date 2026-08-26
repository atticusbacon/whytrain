"""The one screen in the stage-1 MVP: enter/edit your profile and current
goal. Deliberately manual-entry only -- the 'Connect Strava' button is a
placeholder so the layout doesn't shift when stage 3 wires it up for real.
"""
from datetime import date, timedelta

import streamlit as st
from pydantic import ValidationError

from app.models import (
    AthleteProfile,
    DataSource,
    DistanceUnit,
    ExperienceLevel,
    Goal,
    RaceDistance,
)
from app.storage import get_latest_goal, get_latest_profile, upsert_goal, upsert_profile


def render() -> None:
    st.title("Athlete profile & goal")
    st.caption(
        "This is context for explaining how to execute your training -- "
        "not an assessment of how it's going. That call is yours or your coach's."
    )

    existing_profile = get_latest_profile()
    existing_goal = (
        get_latest_goal(existing_profile.id) if existing_profile else None
    )

    _render_profile_section(existing_profile)
    st.divider()
    _render_goal_section(existing_profile)


def _render_profile_section(existing: AthleteProfile | None) -> None:
    st.subheader("Profile")

    if existing and existing.data_source.value != "manual":
        st.info(f"History source: {existing.data_source.value.title()} (connected)")
    else:
        st.button(
            "Connect Strava",
            disabled=True,
            help="Coming in a later stage -- manual entry only for now.",
        )

    with st.form("profile_form"):
        name = st.text_input("Name", value=existing.name if existing else "")

        experience = st.selectbox(
            "Experience level",
            options=list(ExperienceLevel),
            format_func=lambda e: e.value.title(),
            index=list(ExperienceLevel).index(existing.experience_level) if existing else 0,
        )

        unit = st.radio(
            "Preferred unit",
            options=list(DistanceUnit),
            format_func=lambda u: "Miles" if u == DistanceUnit.MILES else "Kilometers",
            index=list(DistanceUnit).index(existing.preferred_unit) if existing else 0,
            horizontal=True,
        )

        mileage = st.number_input(
            "Current weekly mileage",
            min_value=0.0,
            max_value=300.0,
            value=existing.current_weekly_mileage if existing else 20.0,
            step=1.0,
        )

        submitted = st.form_submit_button("Save profile")

    if submitted:
        try:
            profile = AthleteProfile(
                id=existing.id if existing else None,
                name=name,
                experience_level=experience,
                current_weekly_mileage=mileage,
                preferred_unit=unit,
                data_source=existing.data_source if existing else DataSource.MANUAL,
            )
            saved_id = upsert_profile(profile)
            st.success("Profile saved.")
            st.session_state["profile_id"] = saved_id
            st.rerun()
        except ValidationError as e:
            for err in e.errors():
                st.error(f"{err['loc'][0]}: {err['msg']}")


def _render_goal_section(profile: AthleteProfile | None) -> None:
    st.subheader("Current goal")

    if profile is None:
        st.info("Save your profile first, then set a goal.")
        return

    existing_goal = get_latest_goal(profile.id)

    with st.form("goal_form"):
        distance = st.selectbox(
            "Race distance",
            options=list(RaceDistance),
            format_func=lambda d: d.value.replace("_", " ").title(),
            index=list(RaceDistance).index(existing_goal.race_distance) if existing_goal else 3,
        )

        target_date = st.date_input(
            "Target race date",
            value=existing_goal.target_date if existing_goal else date.today() + timedelta(weeks=12),
            min_value=date.today(),
        )

        target_time = st.text_input(
            "Target finish time (optional, H:MM:SS)",
            value=existing_goal.target_time if existing_goal and existing_goal.target_time else "",
            placeholder="e.g. 3:30:00",
        )

        notes = st.text_area(
            "Context for the goal (optional)",
            value=existing_goal.notes if existing_goal and existing_goal.notes else "",
            placeholder="e.g. first marathon, coming back from a break, chasing a Boston qualifier",
        )

        submitted = st.form_submit_button("Save goal")

    if submitted:
        try:
            goal = Goal(
                id=existing_goal.id if existing_goal else None,
                athlete_id=profile.id,
                race_distance=distance,
                target_date=target_date,
                target_time=target_time or None,
                notes=notes or None,
            )
            upsert_goal(goal)
            st.success("Goal saved.")
            st.rerun()
        except ValidationError as e:
            for err in e.errors():
                st.error(f"{err['loc'][0]}: {err['msg']}")
