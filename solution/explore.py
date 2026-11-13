import polars as pl

pl.Config.set_tbl_rows(30)

DATA = "../source-data"


races = pl.read_csv(f"{DATA}/races.csv")


# 2. Reading and looking

# print(races.schema)
# print(races.head(3))
# print(races.shape)
# print(races.columns)
# print(races.describe())
# print(races.null_count())

races = pl.read_csv(
    f"{DATA}/races.csv",
    schema_overrides={"date": pl.Date},
)

print(races.describe())

# quick note, many read_csv options can be found in the docs, null_values can be provided with a
# str, list or dict to dicate which values to replace with null

# 3. The five verbs
