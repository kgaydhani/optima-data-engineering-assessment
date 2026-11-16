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

**Why the original IDs are correct:**
- The extra rows claim positions other drivers already hold.
- Each driver's gap to the winner only fits the original position.
- A race awards at most 101 points. With the extra rows, the two races total 117 and 113.
  Without them, both total 101.

**Impact if ignored:** those drivers get extra points and the 2023 standings order changes.

**Decision:** drop the 3 rows by ID as it is certain these are erroneous. A listed row is only
dropped while it is still a duplicate, so if the client reissued the file with different IDs, a
good row couldn't be lost; the run also logs a warning if it doesn't drop exactly 3 rows.
Any new duplicate stops the run with an error, since it is not possible to know which column may
be problematic without investigation.

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

- **Results:** every race has exactly 20 results once the duplicate rows are removed.

## Checks on every run

These are not one-off: the pipeline re-checks them every time it runs (`validate.py`). If any
fails, it lists every problem found, exits with code 1, and writes no output files.

| Check | Why |
|---|---|
| Columns the outputs use have no blanks | A blank name or date would reach the JSON as `null` |
| Keys are unique: races, (season, round), (raceId, driverId), drivers, teams | A duplicate key double counts points or duplicates rows in a join |
| Every race, driver and team in results exists | A missing link would silently drop a driver from the standings |
| Points match the finishing position | Standings use the source points |
| Every race with results has exactly one winner | Race stats need one winner |
| Finishing positions in each race run 1, 2, 3 ... N | A repeat, gap or position 0 would break countback |
| Lap times are in `m:ss.s` format | So they can be compared as durations |

The pipeline also logs a warning for races in the calendar that have no results yet. These are
left out of the stats, so a run part way through a season shows the races so far.

Columns that are allowed to be blank: `time` (filled with `00:00:00`), `position` (drivers who
didn't finish) and `fastestLapTime` (the output is null if no driver recorded one).

## Not used by the outputs

`qualifying.csv` and `videos.csv` aren't needed for the outputs, so the pipeline doesn't read
them. Profiling found nothing that would matter if they were used later: every link in
`qualifying.csv` resolves, and in `videos.csv` the 5 newest videos have no views, likes or
comments yet, while blank race and driver links are expected (off-season and non-driver videos).
