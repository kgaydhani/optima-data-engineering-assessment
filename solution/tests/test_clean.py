from datetime import date, datetime, time

import polars as pl

from boxbox_pipeline.clean import add_race_start, drop_known_bad_results


def test_drop_known_bad_results_removes_the_bad_twin_and_keeps_the_original():
    # 10272 and 110272 are the same driver in the same race; 110272 is the known bad one.
    results = pl.DataFrame(
        {"resultId": [10272, 110272, 10279], "raceId": [1, 1, 1], "driverId": [12, 12, 19]}
    )

    cleaned = drop_known_bad_results(results)

    assert cleaned["resultId"].to_list() == [10272, 10279]


def test_drop_known_bad_results_keeps_a_listed_id_that_is_no_longer_a_duplicate():
    # If the client reissued the file and 110272 became a genuine, unique row, keep it.
    results = pl.DataFrame({"resultId": [110272], "raceId": [1], "driverId": [12]})

    cleaned = drop_known_bad_results(results)

    assert cleaned["resultId"].to_list() == [110272]


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
