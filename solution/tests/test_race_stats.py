from datetime import datetime

import polars as pl

from boxbox_pipeline.race_stats import build_race_stats, lap_seconds


def make_races():
    return pl.DataFrame(
        {
            "raceId": [1, 2],
            "season": [2024, 2024],
            "round": [1, 2],
            "raceName": ["First GP", "Second GP"],
            "raceStart": [datetime(2024, 3, 10, 13, 0), datetime(2024, 3, 23, 0, 0)],
        }
    )


def test_lap_seconds_converts_minutes_and_seconds():
    laps = pl.DataFrame({"lap": ["1:24.6", "10:01.0"]})

    seconds = laps.select(lap_seconds(pl.col("lap")))["lap"].to_list()

    assert seconds == [84.6, 601.0]


def test_fastest_lap_compares_durations_not_text():
    results = pl.DataFrame(
        {
            "raceId": [1, 1],
            "driverId": [7, 8],
            "position": [1, 2],
            "fastestLapTime": ["10:01.0", "9:59.9"],
        }
    )

    stats = build_race_stats(make_races(), results)

    assert stats["Race Fastest Lap"].to_list() == ["9:59.9"]


def test_race_with_no_lap_recorded_gets_null_fastest_lap():
    results = pl.DataFrame(
        {"raceId": [1], "driverId": [7], "position": [1], "fastestLapTime": [None]},
        schema={
            "raceId": pl.Int64,
            "driverId": pl.Int64,
            "position": pl.Int64,
            "fastestLapTime": pl.String,
        },
    )

    stats = build_race_stats(make_races(), results)

    assert stats["Race Fastest Lap"].to_list() == [None]


def test_output_has_winner_and_brief_datetime_format():
    results = pl.DataFrame(
        {
            "raceId": [1, 1],
            "driverId": [7, 8],
            "position": [2, 1],
            "fastestLapTime": ["1:25.0", "1:24.6"],
        }
    )

    stats = build_race_stats(make_races(), results)

    assert stats.drop("season").to_dicts() == [
        {
            "Race Name": "First GP",
            "Race Round": 1,
            "Race Datetime": "2024-03-10T13:00:00.000",
            "Race Winning driverId": 8,
            "Race Fastest Lap": "1:24.6",
        }
    ]
