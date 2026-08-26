import streamlit as st

from app.storage import init_db
from app.ui import goal_builder

st.set_page_config(page_title="Running widget", page_icon="🏃", layout="centered")

init_db()
goal_builder.render()
