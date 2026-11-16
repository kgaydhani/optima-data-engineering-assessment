# Box Box Analytics: race data pipeline

A Python pipeline that reads the championship CSVs in `source-data/`, checks them, and writes
race stats and driver standings for every season to `results/`.

## Run it

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.13 and the exact package versions
from `uv.lock`, so the environment matches my own.

```
cd solution
uv run python main.py
```

This writes `stats_{season}.json` and `standings_{season}.json` for 2023, 2024 and 2025 to
`results/`. It works from any folder, because paths are built from the code's own location.

If the source data fails validation, the run stops, logs every problem it found, exits with
code 1, and writes nothing, so the previous good files stay in place.

```
uv run pytest            # tests
uv run ruff check .      # lint
```

CI runs lint, format check, tests and the pipeline on every push.

## Requirements

| Requirement | Status |
|---|---|
| Race stats, `stats_{season}.json` | Done |
| Driver standings, `standings_{season}.json`, with countback | Done |
| Python, in `solution/`, run by `main.py` | Done |
| Treat the data as untrusted, investigate it, make decisions explicit | Done: [DATA_QUALITY.md](DATA_QUALITY.md) |
| README with how to run and decisions | This file |
| Stretch: unit tests for all functions | Done: `tests/` |
| Stretch: data quality report | Done: [DATA_QUALITY.md](DATA_QUALITY.md) |
| Stretch: cloud deployment notes | Done: [DEPLOYMENT.md](DEPLOYMENT.md) |

## How it works

An ETL pipeline in a small medallion shape: raw, then clean and checked, then outputs.

| Step | Module | What it does |
|---|---|---|
| Extract | `extract.py` | Reads the four CSVs the outputs need, with explicit schemas. A missing or extra column, or a value of the wrong type, fails the run. |
| Clean | `clean.py` | Applies the data quality decisions: drops the 3 known bad result rows and builds the race start datetime. |
| Validate | `validate.py` | Checks keys, links, points and finishing positions. Collects every problem and raises one error listing them all. |
| Transform | `race_stats.py`, `standings.py` | Builds the two output tables. |
| Load | `load.py` | Writes one JSON file per season. |

`pipeline.py` runs the steps in order and logs row counts. Everything between extract and load
takes DataFrames and returns DataFrames, with no file access, so each step is tested on small
hand-built tables.

## Decisions

Data issues and how each is handled are in [DATA_QUALITY.md](DATA_QUALITY.md). Decisions about
the outputs:

- **Fastest lap:** lap times are compared as durations, not text (as text, `"10:01.0"` sorts
  before `"9:59.9"`). The output is the original text, e.g. `"1:24.6"`, or null if no driver in
  the race recorded one.
- **Race datetime:** the source dates and times are UTC, so there is no timezone conversion and
  no suffix, matching the brief's example. A missing time becomes `00:00:00`.
- **Races without results** (scheduled but not yet run) are left out of the stats, so the
  pipeline can run mid-season and show the races so far. The run logs a warning listing them.
- **Who is in the standings:** every driver with at least one result that season, including
  drivers who scored no points.
- **Countback:** points, then wins, then 2nd places, and so on down every finishing position. If
  two drivers were tied on all of that, the lower `driverId` goes first so the order is always
  the same. This never happens in the current data.
- **Team name:** the team from the driver's latest round that season.
- **Points** come from the source and are checked against the 25-18-15-12-10-8-6-4-2-1 scale on
  every run, rather than recalculated.

## Why Polars

I come from SQL, and Polars' expression API maps closely onto both SQL and PySpark. It is fast,
and strict about types, which suits untrusted data. The data is small, so the pipeline runs
eagerly on one machine. If the volume grew, the same transformations translate almost line for
line to PySpark on Databricks (see [DEPLOYMENT.md](DEPLOYMENT.md)).

## Testing

Unit tests build small tables by hand to cover the cases the real data doesn't have: a lap time
over 10 minutes, a race with no lap time, a points tie decided on 2nd places, a mid-season team
change, positions restarting each season, and each validation check failing. Two end-to-end
tests run the real data: one checks the brief's two example records come out exactly, the
other checks a new duplicate stops the run and writes nothing.

## What I'd do next

- Write the files atomically (to a temporary location, then swap them in), so a failure part way
  through writing can't leave a mix of old and new files, and remove files for seasons that no
  longer exist in the source.
- Write outputs to Delta tables as well as JSON, so analysts can query history.
- Alerting on validation failures, so someone is told when a delivery is rejected.
- In a team: pre-commit hooks for faster local feedback, and branch protection so nothing reaches
  `main` without passing CI and a review.

## How I used AI

Optima is an AI-forward consultancy, and we live in an AI-forward world, so it would have felt
strange to pretend I hadn't used it here. I also appreciate that this is an assesment to see my own
code and how I work through a problem, thus I wrote the core logic myself and worked through the
hard parts rather than handing them off. I am confident I can defend every line in this repo,
and expect this is the point of the interview section of this assessment.
However, I did use AI in the following capacities:

- **As a tutor.** I come from SQL and Snowflake and hadn't used Polars before, so I used Claude
  to learn it, exploring and testing Polars on the source data over the weekend.
- **As a reviewer.** It reviewed my code as I went and challenged my decisions, like making me
  prove which duplicate rows were wrong with evidence instead of just keeping the first.
- **For the mechanical parts.** It drafted the tooling, CI, the load and pipeline wiring, some of
  the tests, and first drafts of these docs, which I have since edited.

I did the data investigation, made every handling decision, and wrote the core logic myself: the
race stats, the standings countback and most of the validation. The outputs were checked against
independently built reference results, and a separate AI session reviewed the code before I
submitted; the gaps it found are fixed and tested. (This is assessment data, so using AI on it was
fine. With real client data I'd stick to approved tools.)
