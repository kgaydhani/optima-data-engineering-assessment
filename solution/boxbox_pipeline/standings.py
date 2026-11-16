"""Standings: final championship table per season (gold layer)."""

import polars as pl


def build_standings(
    races: pl.DataFrame, results: pl.DataFrame, drivers: pl.DataFrame, teams: pl.DataFrame
) -> pl.DataFrame:
    """Rank drivers per season by points, then countback on finishing positions."""
    max_position = results["position"].max()
    position_counts = [
        (pl.col("position") == i).sum().alias(f"p{i}") for i in range(1, max_position + 1)
    ]
    countback = [f"p{i}" for i in range(1, max_position + 1)]

    totals = (
        results.join(races, on="raceId")
        .group_by("season", "driverId")
        .agg(
            pl.col("points").sum().alias("points"),
            *position_counts,
            pl.col("teamId").sort_by("round", descending=True).first(),
        )
        .join(teams, on="teamId")
        .join(drivers, on="driverId")
        .with_columns(
            pl.concat_str(["forename", "surname"], separator=" ").alias("driverName"),
        )
        # Countback: points, then wins, then 2nds, and so on. driverId only if tied on everything.
        .sort(
            ["season", "points", *countback, "driverId"],
            descending=[False, True, *[True] * len(countback), False],
        )
        # ROW_NUMBER() OVER (PARTITION BY season), with the ORDER BY coming from the sort
        .with_columns((pl.int_range(pl.len()).over("season") + 1).alias("position"))
        .select(
            "season",
            "position",
            "driverId",
            "driverName",
            "teamName",
            "points",
            pl.col("p1").alias("wins"),
        )
    )
    return totals
