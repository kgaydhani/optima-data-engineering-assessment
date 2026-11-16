"""Clean: apply data quality decisions (silver layer)."""

from datetime import time

import polars as pl

from boxbox_pipeline.config import KNOWN_BAD_RESULT_IDS


def drop_known_bad_results(results: pl.DataFrame) -> pl.DataFrame:
    """Remove the duplicate result rows shown to be wrong (DATA_QUALITY.md, finding 1)."""
    # Only drop a listed row while it's still a duplicate, so a reissued file can't lose a good row.
    is_known_bad = pl.col("resultId").is_in(KNOWN_BAD_RESULT_IDS)
    is_duplicate = pl.struct("raceId", "driverId").is_duplicated()
    return results.filter(~(is_known_bad & is_duplicate))


def add_race_start(races: pl.DataFrame) -> pl.DataFrame:
    """Add a raceStart datetime, using 00:00:00 when the race time is missing (finding 2)."""
    return races.with_columns(
        # COALESCE(time, '00:00:00') then TIMESTAMP(date, time)
        pl.col("date").dt.combine(pl.col("time").fill_null(time(0, 0))).alias("raceStart")
    )
