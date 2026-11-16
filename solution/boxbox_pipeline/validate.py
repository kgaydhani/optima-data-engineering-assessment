"""Validate: stop the run if the cleaned data breaks a rule the outputs depend on."""

import polars as pl

from boxbox_pipeline.config import POINTS_BY_POSITION


class DataQualityError(Exception):
    """Raised when the source data fails a check the outputs depend on."""


def check_unique(df: pl.DataFrame, key: list[str], table: str) -> list[str]:
    """The given key columns should identify exactly one row of the table."""
    duplicates = df.filter(pl.struct(key).is_duplicated())
    if duplicates.height > 0:
        return [f"{table}: {duplicates.height} rows share a {key}: {duplicates}"]
    return []


def check_foreign_keys(
    races: pl.DataFrame, results: pl.DataFrame, drivers: pl.DataFrame, teams: pl.DataFrame
) -> list[str]:
    """Every race, driver and team in results should exist in its own table."""
    links = [
        ("results -> races", results, "raceId", races),
        ("results -> drivers", results, "driverId", drivers),
        ("results -> teams", results, "teamId", teams),
    ]
    problems = []
    for name, child, key, parent in links:
        orphans = child.join(parent, on=key, how="anti").height
        if orphans > 0:
            problems.append(f"{name}: {orphans} rows with no match")
    return problems


def check_points_match_position(results: pl.DataFrame) -> list[str]:
    """Each row's points should match its finishing position."""
    scale = pl.DataFrame(
        {
            "position": list(POINTS_BY_POSITION.keys()),
            "expected": list(POINTS_BY_POSITION.values()),
        }
    )

    mismatch = (
        results.join(scale, on="position", how="left")
        .with_columns(pl.col("expected").fill_null(0))
        .filter(pl.col("points") != pl.col("expected"))
    )
    if mismatch.height > 0:
        return [f"{mismatch.height} result rows have a point mismatch: {mismatch}"]
    return []


def check_one_winner_per_race(results: pl.DataFrame) -> list[str]:
    """Every race with results should have exactly one driver in position 1."""
    winners = results.group_by("raceId").agg((pl.col("position") == 1).sum().alias("winners"))
    bad = winners.filter(pl.col("winners") != 1)
    if bad.height > 0:
        return [f"{bad.height} races do not have exactly one winner: {bad}"]
    return []


def validate(
    races: pl.DataFrame, results: pl.DataFrame, drivers: pl.DataFrame, teams: pl.DataFrame
) -> None:
    """Run every check and raise DataQualityError listing all problems found."""
    problems = (
        check_unique(races, ["raceId"], "races")
        + check_unique(races, ["season", "round"], "races")
        + check_unique(results, ["raceId", "driverId"], "results")
        + check_unique(drivers, ["driverId"], "drivers")
        + check_unique(teams, ["teamId"], "teams")
        + check_foreign_keys(races, results, drivers, teams)
        + check_points_match_position(results)
        + check_one_winner_per_race(results)
    )
    if problems:
        raise DataQualityError("Source data failed validation:\n- " + "\n- ".join(problems))
