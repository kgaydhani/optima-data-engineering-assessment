# Deployment notes

How I would run this pipeline in the cloud, after every race. I've chosen Databricks, with a
simpler alternative at the end.

## The shape

```
Client drops CSVs  ->  landing volume  ->  Databricks job  ->  Delta tables + JSON files
                       (Unity Catalog)     (this pipeline)     (analysts, video team)
```

1. **Landing.** The client uploads each delivery to a Unity Catalog volume, one folder per
   delivery. Raw files are never changed, so any run can be repeated.
2. **Trigger.** A Databricks job with a **file arrival trigger** starts when a new delivery
   lands, so the outputs are ready straight after each race without anyone running anything.
3. **Run.** The job runs this package as a Python wheel task. The data is small, so a single-node
   or serverless jobs compute is enough and cheap; a full Spark cluster would spend longer
   starting than the pipeline takes to run.
4. **Outputs.** Write the race stats and standings to Delta tables (for analysts, with history
   through time travel) and the JSON files the brief asks for (for the video team).

## Packaging and CI/CD

- Package with a **Databricks Asset Bundle**: the job, its trigger and compute are defined in
  YAML in the repo, next to the code.
- **GitHub Actions** already runs lint and tests on every push. On merge to `main`, it would also
  deploy the bundle: to a dev workspace first, then to production.
- `uv.lock` pins every dependency, so the job runs exactly what was tested.

## Failure handling

- If validation fails, the pipeline raises `DataQualityError`, exits with code 1 and writes
  nothing. The job is marked failed and an **email or Slack alert** goes to the data team, with
  the list of problems in the job log.
- Because nothing is written on failure, the analysts keep the last good outputs. A wrong
  standings table is worse than a late one.
- Reruns are safe: each run rebuilds the outputs from the full source and overwrites them, so
  running twice gives the same result.

## Governance

- **Unity Catalog** controls who can read the raw volume and the output tables, and records
  lineage from the source files to each table.
- The client's raw files and our outputs live in separate schemas, so analysts never read
  unchecked data.

## When the data grows

The current data is three seasons of one series. If Box Box added more series or much more
history:
- Switch Polars to its lazy mode (`scan_csv` and `collect`), which only reads the columns and rows
  each step needs.
- Beyond one machine, move the transformations to PySpark. The logic is the same filters, joins,
  group-bys and window functions, so it is a translation, not a redesign.
- Process only new races and append to the Delta tables, instead of rebuilding everything.

## A simpler alternative

If Box Box doesn't already use Databricks, a cheaper option is an AWS Lambda (or Azure Function)
triggered by an upload to S3, writing the JSON back to S3. It costs almost nothing at this size
and needs no platform. The trade-off: no built-in lineage, scheduling, Delta history or
governance, which matter once more people and more data are involved.
