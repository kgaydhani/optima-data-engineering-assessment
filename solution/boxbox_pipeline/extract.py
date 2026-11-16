"""Extract: read the source CSVs with explicit schemas (bronze layer)."""

from dataclasses import dataclass
from pathlib import Path

import polars as pl

RACES_SCHEMA = {
    # raceId,season,round,raceName,circuit,country,date,time
    "raceId": pl.Int64,
    "season": pl.Int64,
    "round": pl.Int64,
    "raceName": pl.String,
    "circuit": pl.String,
    "country": pl.String,
    "date": pl.Date,
    "time": pl.Time,
}

RESULTS_SCHEMA = {
    # resultId,raceId,driverId,teamId,grid,position,points,status,fastestLapTime,gapToWinnerSeconds
    "resultId": pl.Int64,
    "raceId": pl.Int64,
    "driverId": pl.Int64,
    "teamId": pl.Int64,
    "grid": pl.Int64,
    "position": pl.Int64,
    "points": pl.Int64,
    "status": pl.String,
    "fastestLapTime": pl.String,
    "gapToWinnerSeconds": pl.Float64,
}

DRIVERS_SCHEMA = {
    # driverId,code,forename,surname,nationality,dateOfBirth
    "driverId": pl.Int64,
    "code": pl.String,
    "forename": pl.String,
    "surname": pl.String,
    "nationality": pl.String,
    "dateOfBirth": pl.Date,
}

TEAMS_SCHEMA = {
    # teamId,teamName,engineSupplier
    "teamId": pl.Int64,
    "teamName": pl.String,
    "engineSupplier": pl.String,
}


@dataclass(frozen=True)
class SourceTables:
    """The raw tables the pipeline needs."""

    races: pl.DataFrame
    results: pl.DataFrame
    drivers: pl.DataFrame
    teams: pl.DataFrame


def read_sources(data_dir: Path) -> SourceTables:
    """Read each source CSV, failing if any column or value doesn't match its schema."""
    return SourceTables(
        races=pl.read_csv(
            data_dir / "races.csv",
            schema=RACES_SCHEMA,
            null_values={"time": "null"},  # see DATA_QUALITY.md, finding 2
        ),
        results=pl.read_csv(data_dir / "results.csv", schema=RESULTS_SCHEMA),
        drivers=pl.read_csv(data_dir / "drivers.csv", schema=DRIVERS_SCHEMA),
        teams=pl.read_csv(data_dir / "teams.csv", schema=TEAMS_SCHEMA),
    )
