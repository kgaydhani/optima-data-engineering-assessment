import shutil

import polars as pl
import pytest

from boxbox_pipeline.config import SOURCE_DATA_DIR
from boxbox_pipeline.extract import read_sources


def test_read_sources_reads_the_text_null_in_race_time_as_missing():
    tables = read_sources(SOURCE_DATA_DIR)

    assert tables.races.schema["time"] == pl.Time
    assert tables.races["time"].null_count() == 8


def test_read_sources_fails_on_a_value_that_does_not_match_the_schema(tmp_path):
    data_dir = tmp_path / "source-data"
    shutil.copytree(SOURCE_DATA_DIR, data_dir)
    (data_dir / "teams.csv").write_text(
        "teamId,teamName,engineSupplier\nnot-a-number,Red,Titan\n", encoding="utf-8"
    )

    with pytest.raises(pl.exceptions.PolarsError):
        read_sources(data_dir)
