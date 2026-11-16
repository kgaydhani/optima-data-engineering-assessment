"""Pipeline settings: paths and known data corrections."""

from pathlib import Path

# This file lives at <repo>/solution/boxbox_pipeline/config.py, so the repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DATA_DIR = REPO_ROOT / "source-data"
RESULTS_DIR = REPO_ROOT / "results"

# Duplicate result rows shown to be wrong. Evidence in DATA_QUALITY.md, finding 1.
KNOWN_BAD_RESULT_IDS = frozenset({110272, 110279, 111383})
