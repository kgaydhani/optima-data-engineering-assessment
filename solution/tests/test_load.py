import json

import polars as pl

from boxbox_pipeline.load import write_season_files


def test_write_season_files_writes_one_file_per_season_without_the_season_column(tmp_path):
    table = pl.DataFrame({"season": [2024, 2023, 2024], "position": [1, 1, 2]})

    write_season_files(table, "standings", tmp_path)

    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "standings_2023.json",
        "standings_2024.json",
    ]
    records = json.loads((tmp_path / "standings_2024.json").read_text(encoding="utf-8"))
    assert records == [{"position": 1}, {"position": 2}]


def test_write_season_files_uses_unix_line_endings(tmp_path):
    table = pl.DataFrame({"season": [2024], "position": [1]})

    write_season_files(table, "standings", tmp_path)

    assert b"\r\n" not in (tmp_path / "standings_2024.json").read_bytes()
