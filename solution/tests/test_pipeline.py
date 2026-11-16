import json
import shutil

import pytest

from boxbox_pipeline.config import SOURCE_DATA_DIR
from boxbox_pipeline.pipeline import run
from boxbox_pipeline.validate import DataQualityError


def test_pipeline_reproduces_the_brief_examples(tmp_path):
    run(SOURCE_DATA_DIR, tmp_path)

    assert sorted(p.name for p in tmp_path.iterdir()) == [
        f"{kind}_{season}.json" for kind in ("standings", "stats") for season in (2023, 2024, 2025)
    ]
    stats_2024 = json.loads((tmp_path / "stats_2024.json").read_text(encoding="utf-8"))
    standings_2024 = json.loads((tmp_path / "standings_2024.json").read_text(encoding="utf-8"))
    assert stats_2024[0] == {
        "Race Name": "Silverpine Grand Prix",
        "Race Round": 1,
        "Race Datetime": "2024-03-10T13:00:00.000",
        "Race Winning driverId": 2,
        "Race Fastest Lap": "1:24.6",
    }
    assert standings_2024[0] == {
        "position": 1,
        "driverId": 1,
        "driverName": "Kasper Renn",
        "teamName": "Meridian Racing",
        "points": 389,
        "wins": 10,
    }


def test_pipeline_writes_nothing_when_validation_fails(tmp_path):
    data_dir = tmp_path / "source-data"
    results_dir = tmp_path / "results"
    shutil.copytree(SOURCE_DATA_DIR, data_dir)
    # Add a new, uninvestigated duplicate, the first result row again with a new resultId.
    results_csv = data_dir / "results.csv"
    first_row = results_csv.read_text(encoding="utf-8").splitlines()[1]
    duplicate = "99999" + first_row[first_row.index(",") :]
    with results_csv.open("a", encoding="utf-8") as f:
        f.write(duplicate + "\n")

    with pytest.raises(DataQualityError):
        run(data_dir, results_dir)

    assert not results_dir.exists()
