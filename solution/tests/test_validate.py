import polars as pl
import pytest

from boxbox_pipeline.validate import (
    DataQualityError,
    check_finishing_positions,
    check_foreign_keys,
    check_one_winner_per_race,
    check_points_match_position,
    check_unique,
    validate,
)


def test_check_unique_flags_a_repeated_key():
    results = pl.DataFrame({"raceId": [1, 1, 2], "driverId": [7, 7, 7]})

    problems = check_unique(results, ["raceId", "driverId"], "results")

    assert len(problems) == 1


def test_check_unique_passes_when_every_key_is_different():
    results = pl.DataFrame({"raceId": [1, 1, 2], "driverId": [7, 8, 7]})

    assert check_unique(results, ["raceId", "driverId"], "results") == []


def test_check_foreign_keys_flags_a_driver_that_does_not_exist():
    results = pl.DataFrame({"raceId": [1], "driverId": [1], "teamId": [1]})
    races = pl.DataFrame({"raceId": [1]})
    drivers = pl.DataFrame({"driverId": [2]})
    teams = pl.DataFrame({"teamId": [1]})

    problems = check_foreign_keys(races, results, drivers, teams)

    assert len(problems) == 1
    assert "drivers" in problems[0]


def test_check_foreign_keys_passes_when_all_foreign_keys_exist():
    results = pl.DataFrame({"raceId": [1], "driverId": [1], "teamId": [1]})
    races = pl.DataFrame({"raceId": [1]})
    drivers = pl.DataFrame({"driverId": [1]})
    teams = pl.DataFrame({"teamId": [1]})

    problems = check_foreign_keys(races, results, drivers, teams)

    assert problems == []


def test_check_points_match_position_passes_matching_pairs():
    results = pl.DataFrame(
        {"position": [1, 2, None, 12], "points": [25, 18, 0, 0]},
        schema={"position": pl.Int64, "points": pl.Int64},
    )

    assert check_points_match_position(results) == []


def test_check_points_match_position_flags_missing_points():
    results = pl.DataFrame(
        {"position": [1], "points": [None]},
        schema={"position": pl.Int64, "points": pl.Int64},
    )

    problems = check_points_match_position(results)

    assert len(problems) == 1
    assert "1 result rows" in problems[0]


def test_check_points_match_position_flags_incorrect_points():
    results = pl.DataFrame(
        {"position": [1], "points": [11]},
        schema={"position": pl.Int64, "points": pl.Int64},
    )

    problems = check_points_match_position(results)

    assert len(problems) == 1
    assert "1 result rows" in problems[0]


def test_check_one_winner_per_race_passes_when_one_winner():
    results = pl.DataFrame({"raceId": [1, 2, 3, 1], "position": [2, 1, 1, 1]})

    assert check_one_winner_per_race(results) == []


def test_check_one_winner_per_race_flags_when_no_winner():
    results = pl.DataFrame({"raceId": [1, 1, 1], "position": [2, 3, 6]})

    problems = check_one_winner_per_race(results)

    assert len(problems) == 1
    assert "1 races" in problems[0]


def test_check_one_winner_per_race_flags_when_two_winners():
    results = pl.DataFrame({"raceId": [1, 1, 1], "position": [1, 3, 1]})

    problems = check_one_winner_per_race(results)

    assert len(problems) == 1
    assert "1 races" in problems[0]


def test_check_finishing_positions_passes_when_correct_positions():
    results = pl.DataFrame({"raceId": [1, 1, 1, 1], "position": [1, 2, 3, None]})

    assert check_finishing_positions(results) == []


def test_check_finishing_positions_flags_a_repeated_position():
    results = pl.DataFrame({"raceId": [1, 1, 1], "position": [1, 2, 2]})

    problems = check_finishing_positions(results)

    assert len(problems) == 1
    assert "1 races" in problems[0]


def test_check_finishing_positions_flags_a_gap_in_positions():
    results = pl.DataFrame({"raceId": [1, 1, 1], "position": [1, 2, 4]})

    problems = check_finishing_positions(results)

    assert len(problems) == 1
    assert "1 races" in problems[0]


def make_valid_tables():
    races = pl.DataFrame({"raceId": [1], "season": [2024], "round": [1]})
    results = pl.DataFrame(
        {
            "raceId": [1, 1],
            "driverId": [10, 20],
            "teamId": [100, 100],
            "position": [1, 2],
            "points": [25, 18],
        }
    )
    drivers = pl.DataFrame({"driverId": [10, 20]})
    teams = pl.DataFrame({"teamId": [100]})
    return races, results, drivers, teams


def test_validate_passes_on_valid_tables():
    races, results, drivers, teams = make_valid_tables()

    validate(races, results, drivers, teams)


def test_validate_raises_and_lists_every_problem():
    races, results, drivers, teams = make_valid_tables()
    results = pl.concat([results, results.head(1)])
    drivers = pl.DataFrame({"driverId": [10]})

    with pytest.raises(DataQualityError) as error:
        validate(races, results, drivers, teams)

    message = str(error.value)
    assert "results: 2 rows share" in message
    assert "results -> drivers" in message
