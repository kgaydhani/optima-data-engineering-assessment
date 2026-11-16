import polars as pl

from boxbox_pipeline.standings import build_standings

DRIVERS = pl.DataFrame(
    {"driverId": [1, 2, 3], "forename": ["Ann", "Ben", "Cal"], "surname": ["A", "B", "C"]}
)
TEAMS = pl.DataFrame({"teamId": [10, 20], "teamName": ["Red", "Blue"]})


def make_races(n):
    return pl.DataFrame(
        {"raceId": list(range(1, n + 1)), "season": [2024] * n, "round": list(range(1, n + 1))}
    )


def make_results(rows):
    """rows: (raceId, driverId, teamId, position, points)."""
    return pl.DataFrame(
        rows,
        schema={
            "raceId": pl.Int64,
            "driverId": pl.Int64,
            "teamId": pl.Int64,
            "position": pl.Int64,
            "points": pl.Int64,
        },
        orient="row",
    )


def test_countback_breaks_a_tie_on_points_using_second_places():
    # Drivers 1 and 2 both finish on 43 points with one win each.
    # Driver 2 has a 2nd place and driver 1 does not, so driver 2 ranks higher.
    results = make_results(
        [
            (1, 1, 10, 1, 25),
            (1, 2, 20, 2, 18),
            (1, 3, 10, 3, 15),
            (2, 2, 20, 1, 25),
            (2, 3, 10, 2, 18),
            (2, 1, 10, 4, 12),
            (3, 3, 10, 1, 25),
            (3, 1, 10, 6, 6),
            (3, 2, 20, 11, 0),
        ]
    )

    standings = build_standings(make_races(3), results, DRIVERS, TEAMS)

    assert standings.select("driverId", "points", "position").rows() == [
        (3, 58, 1),
        (2, 43, 2),
        (1, 43, 3),
    ]


def test_team_is_taken_from_the_drivers_latest_round():
    results = make_results([(1, 1, 10, 1, 25), (2, 1, 20, 1, 25)])

    standings = build_standings(make_races(2), results, DRIVERS, TEAMS)

    assert standings["teamName"].to_list() == ["Blue"]


def test_positions_restart_for_each_season():
    races = pl.DataFrame({"raceId": [1, 2], "season": [2023, 2024], "round": [1, 1]})
    results = make_results(
        [(1, 1, 10, 1, 25), (1, 2, 20, 2, 18), (2, 2, 20, 1, 25), (2, 1, 10, 2, 18)]
    )

    standings = build_standings(races, results, DRIVERS, TEAMS)

    assert standings.select("season", "driverId", "position").rows() == [
        (2023, 1, 1),
        (2023, 2, 2),
        (2024, 2, 1),
        (2024, 1, 2),
    ]


def test_output_record_matches_the_brief():
    results = make_results([(1, 1, 10, 1, 25), (1, 2, 20, None, 0)])

    standings = build_standings(make_races(1), results, DRIVERS, TEAMS)

    assert standings.drop("season").to_dicts() == [
        {
            "position": 1,
            "driverId": 1,
            "driverName": "Ann A",
            "teamName": "Red",
            "points": 25,
            "wins": 1,
        },
        {
            "position": 2,
            "driverId": 2,
            "driverName": "Ben B",
            "teamName": "Blue",
            "points": 0,
            "wins": 0,
        },
    ]
