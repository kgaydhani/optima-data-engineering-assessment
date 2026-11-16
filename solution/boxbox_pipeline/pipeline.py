"""Pipeline: run extract, clean, validate, build and load in order."""

import logging
from pathlib import Path

from boxbox_pipeline.clean import add_race_start, drop_known_bad_results
from boxbox_pipeline.config import KNOWN_BAD_RESULT_IDS, RESULTS_DIR, SOURCE_DATA_DIR
from boxbox_pipeline.extract import read_sources
from boxbox_pipeline.load import write_season_files
from boxbox_pipeline.race_stats import build_race_stats
from boxbox_pipeline.standings import build_standings
from boxbox_pipeline.validate import validate

logger = logging.getLogger(__name__)


def run(data_dir: Path = SOURCE_DATA_DIR, results_dir: Path = RESULTS_DIR) -> list[Path]:
    """Build every output file from the source data. Nothing is written if validation fails."""
    tables = read_sources(data_dir)
    logger.info(
        "Read %d races, %d results, %d drivers, %d teams",
        tables.races.height,
        tables.results.height,
        tables.drivers.height,
        tables.teams.height,
    )

    results = drop_known_bad_results(tables.results)
    races = add_race_start(tables.races)
    dropped = tables.results.height - results.height
    logger.info("Dropped %d known bad result rows", dropped)
    if dropped != len(KNOWN_BAD_RESULT_IDS):
        logger.warning(
            "Expected to drop %d known bad rows but dropped %d: check whether the file has changed",
            len(KNOWN_BAD_RESULT_IDS),
            dropped,
        )

    validate(races, results, tables.drivers, tables.teams)
    logger.info("Validation passed")

    not_yet_raced = races.join(results, on="raceId", how="anti")
    if not_yet_raced.height > 0:
        logger.warning(
            "%d races have no results yet and are left out of the stats: %s",
            not_yet_raced.height,
            not_yet_raced["raceId"].to_list(),
        )

    stats = build_race_stats(races, results)
    standings = build_standings(races, results, tables.drivers, tables.teams)

    written = write_season_files(stats, "stats", results_dir) + write_season_files(
        standings, "standings", results_dir
    )
    for path in written:
        logger.info("Wrote %s", path.name)
    return written
