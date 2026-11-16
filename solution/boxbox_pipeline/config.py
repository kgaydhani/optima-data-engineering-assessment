"""Pipeline settings: paths and known data corrections."""

from pathlib import Path

# This file lives at <repo>/solution/boxbox_pipeline/config.py, so the repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DATA_DIR = REPO_ROOT / "source-data"
RESULTS_DIR = REPO_ROOT / "results"

# Duplicate result rows shown to be wrong. Evidence in DATA_QUALITY.md, finding 1.
KNOWN_BAD_RESULT_IDS = frozenset({110272, 110279, 111383})

# Points awarded by finishing position (Assignment README). Any other position scores 0.
POINTS_BY_POSITION = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
