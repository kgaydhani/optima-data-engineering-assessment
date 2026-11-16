# Data quality report

All six source files were profiled before building the pipeline. This is what was found and how
the pipeline handles it.

## Summary

| # | Issue | File | Handling |
|---|---|---|---|
| 1 | Conflicting duplicate results | `results.csv` | Drop 3 known bad rows, fail on any new duplicate |
| 2 | Race time is the text `"null"` | `races.csv` | Treat as missing, use `00:00:00` |
| 3 | Mid-season driver change | `results.csv` | No fix, team taken from the driver's latest race |

## 1. Conflicting duplicate results

3 rows repeat a (raceId, driverId) pair with different position and points. Each has the
original ID with a `1` in front.

| raceId | driverId | Original (kept) | Extra (dropped) |
|---|---|---|---|
| 202314 | 19 | 10279: P6, 8 pts | 110279: P5, 10 pts |
| 202314 | 12 | 10272: P8, 4 pts | 110272: P7, 6 pts |
| 202420 | 4 | 11383: P5, 10 pts | 111383: P4, 12 pts |

**Why the originals are right:**
- The extra rows claim positions other drivers already hold.
- Each driver's gap to the winner only fits the original position.
- A race awards at most 101 points. With the extra rows, the two races total 117 and 113.
  Without them, both total 101.

**Impact if ignored:** those drivers get extra points and the 2023 standings order changes.

**Decision:** drop the 3 rows by ID as it is certain these are erroneous.
Any new duplicate stops the run with an error, since it is not possible to know which column may be problematic without investigation.

## 2. Race time is the text `"null"`

8 races in 2023 have the word `"null"` as their time, not an empty cell, so `null_count()`
misses them and datetime parsing fails.

**Decision:** the CSV reader treats `"null"` in the `time` column as missing. The cleaning step
then fills missing times with `00:00:00`, as the brief says.

## 3. Mid-season driver change

In 2024, Tempest Motorsport (team 9) replaced driver 17 (rounds 1 to 12) with driver 22
(rounds 13 to 22). So 2024 has 21 drivers in the standings. No driver changes team within a
season.

**Decision:** nothing to fix. Each driver's team is taken from their latest race of the season,
so a future team change would also be handled.

## Checks that passed

- **Foreign keys:** every race, driver and team ID in `results.csv` and `qualifying.csv`
  exists in its parent file.
- **Points:** every row's points match its position (25, 18, 15, 12, 10, 8, 6, 4, 2, 1, else 0).
  Every race totals 101 points once the duplicate rows are removed.
- **Winners:** every race has exactly one driver in position 1.
- **Status:** drivers with a position all have status `Finished`, and drivers without one don't.
- **Fastest laps:** 152 rows have no lap time, but every race has at least one. All lap times
  use the same `m:ss.s` format.

## Checks on every run

<!-- TODO: fill in once validate.py exists. -->
