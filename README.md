# running-widget

An LLM-backed running training explainer. It does **not** tell you how your
training is going — that's for a coach or your own feel, not a scraped
dataset. Instead it takes a user-defined goal plus training history and
explains *how to execute* workouts and training concepts.

## Project stages

1. **Athlete profile & goal builder UI** (this stage) — capture who the
   runner is and what they're training for.
2. **LetsRun content pipeline** — scrape, clean, and distill forum/article
   content into a structured knowledge base (vector store).
3. **Wearable data integration** — start with Strava, add Garmin/Coros later.
4. **LLM orchestrator** — combine the knowledge base + athlete profile to
   answer "how do I execute this workout / plan" questions, never
   "how is my training going."

## Stage 1: Athlete profile & goal builder

A small Streamlit app that lets a runner enter their profile and current
goal, persisted locally in SQLite. This is deliberately manual-entry first —
Strava OAuth gets wired into the same `AthleteProfile` model in stage 3
without changing this UI's shape.

### Setup

```
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### Run

```
streamlit run app/main.py
```

Data is stored in `data/running_widget.db` (SQLite, gitignored).

### Project layout

```
app/
  models.py        # AthleteProfile, Goal — the shared data contracts
  storage.py        # SQLite persistence (no ORM, plain sqlite3)
  ui/
    goal_builder.py # Streamlit page: profile + goal form
  main.py            # Streamlit entrypoint
tests/
  test_models.py
  test_storage.py
```
