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

# print(races.describe())

# quick note, many read_csv options can be found in the docs, null_values can be provided with a
# str, list or dict to dicate which values to replace with null

# 3. The five verbs

drivers = pl.read_csv(f"{DATA}/drivers.csv")

# print(drivers.select("driverId", "surname"))

# without .alias() below we end up with the first column being concat'd ie. forename as the col name

# print(
#     drivers.select(
#         "driverId",
#         (pl.col("forename") + " " + pl.col("surname")).alias("fullName"),
#     )
# )

# print(
#     drivers.with_columns(
#         pl.concat_str(["forename", "surname"], separator=" ").alias("fullName"),
#         pl.col("dateOfBirth").str.to_date("%Y-%m-%d"),
#     )
# )

# print(drivers)

print(races.filter(pl.col("season") == 2024, pl.col("round") <= 3))

#the same thing, written with & (brackets are required)
# races.filter((pl.col("season") == 2024) & (pl.col("round") <= 3))
# Other useful conditions:
# pl.col("x").is_in([1, 3]), pl.col("x").is_null(), pl.col("x").is_not_null(), and ~ for "not".
