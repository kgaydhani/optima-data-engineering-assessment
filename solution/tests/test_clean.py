from datetime import date, datetime, time

import polars as pl

from boxbox_pipeline.clean import add_race_start, drop_known_bad_results


def test_drop_known_bad_results_removes_only_the_listed_rows():
    results = pl.DataFrame({"resultId": [10272, 110272, 10279]})

    cleaned = drop_known_bad_results(results)

    assert cleaned["resultId"].to_list() == [10272, 10279]


def test_add_race_start_uses_midnight_when_time_is_missing():
    races = pl.DataFrame(
        {"date": [date(2024, 3, 10), date(2023, 3, 18)], "time": [time(13, 0), None]},
        schema={"date": pl.Date, "time": pl.Time},
    )

    result = add_race_start(races)

    assert result["raceStart"].to_list() == [
        datetime(2024, 3, 10, 13, 0),
        datetime(2023, 3, 18, 0, 0),
    ]
