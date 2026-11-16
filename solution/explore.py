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

# races = pl.read_csv(
#     f"{DATA}/races.csv",
#     schema_overrides={"date": pl.Date},
# )

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

# print(races.filter(pl.col("season") == 2024, pl.col("round") <= 3))

# the same thing, written with & (brackets are required)
# races.filter((pl.col("season") == 2024) & (pl.col("round") <= 3))
# Other useful conditions:
# pl.col("x").is_in([1, 3]), pl.col("x").is_null(), pl.col("x").is_not_null(), and ~ for "not".

# print(
#     races.group_by("season")
#     .agg(
#         pl.len().alias("races"),
#         pl.col("date").min().alias("firstRace"),
#     )
#     .sort("season")
# )

quali = pl.read_csv(f"{DATA}/qualifying.csv")

# poles = (
#     quali.filter(pl.col("qPosition") == 1)
#     .join(drivers, on="driverId", how="left")
#     .select("raceId", "surname")
# )

# print(poles)

# print(drivers.sort(["nationality", "surname"], descending=[False, True]))

df = pl.DataFrame({"a": [1, None, 3], "b": ["x", "", None]})

# df.filter(pl.col("a") > 1)
# df.select(
#     pl.col("a").sum().alias("sum"),
#     pl.col("a").count().alias("count"),
#     pl.len(),
# )

# print(df.with_columns(pl.col("a").fill_null(0)))
# df.select(
#     pl.col("b").is_null().sum().alias("nulls"),
#     (pl.col("b") == "").sum().alias("empties"),
# )

# x = pl.DataFrame({"s": ["1", "two"]}).with_columns(pl.col("s").cast(pl.Int64, strict=False))
# print(x)

results = pl.read_csv(f"{DATA}/results.csv")

# results["status"].n_unique()


# x = results.select(pl.all().null_count())

# quali.with_columns(
#     pl.when(pl.col("qPosition") <= 3).then(pl.lit("top3")).otherwise(pl.lit("rest")).alias("band")
# )

# quali.with_columns(pl.col("qPosition").max().over("raceId").alias("fieldSize"))

teams = pl.read_csv(f"{DATA}/teams.csv")

# x = teams.to_dicts()

# x = results.select("points", "teamId").is_duplicated().sum()


# print(results)

# # Which combinations repeat, and how often (like GROUP BY ... HAVING COUNT(*) > 1)
# results.group_by("col1", "col2").agg(pl.len().alias("n")).filter(pl.col("n") > 1)

# # Show the full rows involved, every column, so you can compare them side by side
# x = results.filter(pl.struct("driverId", "raceId").is_duplicated())

# print(x)


# lf = (
#     pl.scan_csv(f"{DATA}/races.csv")  # scan, not read: nothing loaded yet
#     .filter(pl.col("season") == 2025)
#     .select("round", "raceName")
# )
# print(lf.explain())  # the query plan
# print(lf.collect())  # now it runs

# Exercises

# 1. How many races are there in each season?

# races = pl.read_csv(
#     f"{DATA}/races.csv",
#     schema_overrides={"date": pl.Date},
# )

# print(races.group_by("season").agg(pl.len().alias("nRaces")).sort("season"))

# 2. Which driver has the most pole positions (qualifying position 1) across all three seasons?
# Show their full name and the count, top 3 only. (top is Kasper Renn with 51)

quali = pl.read_csv(f"{DATA}/qualifying.csv")

# x = (
#     quali.filter(pl.col("qPosition") == 1)
#     .group_by("driverId")
#     .agg(pl.len().alias("count"))
#     .join(drivers, on="driverId", how="left")
#     .select(
#         (pl.col("forename") + " " + pl.col("surname")).alias("fullName"),
#         "count",
#     )
#     .sort(["count", "fullName"], descending=[True, False])
#     .head(3)
# )

# print(x)

# Which nationality has the most drivers? (Japanese, 2)

drivers = pl.read_csv(f"{DATA}/drivers.csv")

# x = (
#     drivers.group_by("nationality")
#     .agg(pl.len().alias("count"))
#     .filter(pl.col("count") == pl.col("count").max())
# )

# x = drivers.group_by("nationality").agg(pl.len().alias("count")).top_k(1, by="count")

# 4. Use an anti join to check that every driverId in qualifying.csv exists in drivers.csv.
# How many rows have no match?

# dcheck = quali.join(drivers, on="driverId", how="anti")

# print(dcheck)

# print(quali.join(drivers, on="driverId", how="anti").height)  # 0

# 5. How many distinct drivers set a qualifying time in each season?
# (You'll need to join to races to get the season.) Write the answer down, it's a finding.

races = pl.read_csv(f"{DATA}/races.csv")

# x = (
#     quali.join(races, on="raceId", how="left")
#     .group_by("season")
#     .agg(
#         pl.col("driverId").n_unique().alias("drivers"),
#     )
#     .sort("season")
# )


# print(x)

y = (
    results.join(races, on="raceId", how="left")
    .group_by("season", "teamId")
    .agg(pl.col("driverId").n_unique(), pl.col("driverId").unique().alias("drivers"))
    .sort("season", "teamId")
)

print(y)
