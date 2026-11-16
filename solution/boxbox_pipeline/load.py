"""Load: write one JSON file per season."""

import json
from pathlib import Path

import polars as pl


def write_season_files(table: pl.DataFrame, prefix: str, results_dir: Path) -> list[Path]:
    """Write each season's rows to {prefix}_{season}.json, dropping the season helper column."""
    results_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for season in sorted(table["season"].unique().to_list()):
        records = table.filter(pl.col("season") == season).drop("season").to_dicts()
        path = results_dir / f"{prefix}_{season}.json"
        text = json.dumps(records, indent=4, ensure_ascii=False) + "\n"
        # newline="\n" so the file is byte-identical on Windows and Linux.
        path.write_text(text, encoding="utf-8", newline="\n")
        written.append(path)
    return written
