"""Race stats: one record per race (gold layer)."""

import polars as pl


def lap_seconds(lap: pl.Expr) -> pl.Expr:
    """Turn an "m:ss.s" lap time into seconds, so laps compare as numbers, not text."""
    minutes_and_seconds = lap.str.split(":")
    minutes = minutes_and_seconds.list.get(0).cast(pl.Int64)
    seconds = minutes_and_seconds.list.get(1).cast(pl.Float64)
    return minutes * 60 + seconds


def build_race_stats(races: pl.DataFrame, results: pl.DataFrame) -> pl.DataFrame:
    """One row per race with results: name, round, start time, winner and fastest lap."""
    winners = results.filter(pl.col("position") == 1).select(
        "raceId",
        "driverId",
    )
    fastest_laps = (
        results.filter(pl.col("fastestLapTime").is_not_null())
        .with_columns(lap_seconds(pl.col("fastestLapTime")).alias("lapSeconds"))
        .group_by("raceId")
        .agg(pl.col("fastestLapTime").sort_by("lapSeconds").first())
    )
    return (
        races.join(winners, on="raceId", how="inner")
        .join(fastest_laps, on="raceId", how="left")
        .select(
            "season",
            pl.col("raceName").alias("Race Name"),
            pl.col("round").alias("Race Round"),
            pl.col("raceStart").dt.strftime("%Y-%m-%dT%H:%M:%S%.3f").alias("Race Datetime"),
            pl.col("driverId").alias("Race Winning driverId"),
            pl.col("fastestLapTime").alias("Race Fastest Lap"),
        )
        .sort(["season", "Race Round"])
    )
