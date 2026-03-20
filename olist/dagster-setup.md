# Dagster Setup

This project uses [Dagster](https://dagster.io/) to orchestrate dbt model runs. The Dagster
package lives at `my_dbt_dagster_project/` (sibling to `olist/`) and points at this dbt project.

---

## Package Structure

```
my_dbt_dagster_project/
├── setup.py                           # Package definition and dependencies
└── my_dbt_dagster_project/
    ├── assets.py                      # Defines olist_dbt_assets — runs dbt build
    ├── definitions.py                 # Wires assets, schedules, and DbtCliResource
    ├── project.py                     # DbtProject pointing at ../olist
    └── schedules.py                   # Daily schedule (midnight UTC) for all models
```

---

## Installation

From the workspace root, create or update the shared conda environment and then install the Dagster package with dev dependencies:

```bash
conda env create -f environment.spark.yml
conda activate spark
conda env update -f environment.spark.yml --prune
cd /path/to/dsai-module2-project
pip install -e "my_dbt_dagster_project[dev]"
```

This uses the checked-in `environment.spark.yml` file so learners can reproduce the same conda-based setup instead of creating a separate virtual environment. The editable install adds the local Dagster package on top of the shared environment.

---

## Starting the Dagster Server

```bash
conda activate spark
cd my_dbt_dagster_project
dagster dev
```

The Dagster UI will be available at **http://localhost:3000/**

---

## How It Works

### `project.py`

Defines a `DbtProject` that resolves the `olist/` dbt project relative to this package:

```python
olist_project = DbtProject(
    project_dir=Path(__file__).joinpath("..", "..", "..", "olist").resolve(),
    packaged_project_dir=Path(__file__).joinpath("..", "..", "dbt-project").resolve(),
)
olist_project.prepare_if_dev()
```

`prepare_if_dev()` compiles the dbt manifest at startup so Dagster can read the full asset DAG.

### `assets.py`

Defines the `olist_dbt_assets` asset group, which runs `dbt build` (run + test) for all models:

```python
@dbt_assets(manifest=olist_project.manifest_path)
def olist_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```

### `schedules.py`

A daily schedule at midnight UTC materializes all dbt models:

```python
schedules = [
    build_schedule_from_dbt_selection(
        [olist_dbt_assets],
        job_name="materialize_dbt_models",
        cron_schedule="0 0 * * *",
        dbt_select="fqn:*",
    ),
]
```

---

## Incremental Models

The `fact_reviews` model is currently a view. To make it incremental (appending new reviews by
creation date), update the model with an incremental config block:

```sql
{{ config(
    materialized='incremental',
    on_schema_change='fail'
) }}

...existing SELECT...

{% if is_incremental() %}
  AND review_creation_ts > (SELECT MAX(review_creation_ts) FROM {{ this }})
{% endif %}
```

To backfill a specific date range via the dbt CLI:

```bash
dbt run --select fact_reviews --vars '{start_date: "2017-01-01", end_date: "2018-01-01"}'
```

Reference: [dbt incremental models](https://docs.getdbt.com/docs/build/incremental-models#about-incremental_strategy)

---

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| `manifest.json not found` | dbt project not compiled | Run `dbt compile` in `olist/` before starting Dagster |
| `ModuleNotFoundError: dagster_dbt` | Package not installed | Run `pip install -e "my_dbt_dagster_project[dev]"` |
| `Connection refused` on `localhost:3000` | Dagster server not running | Run `dagster dev` from `my_dbt_dagster_project/` |
| dbt models fail in Dagster | Snowflake auth issue | Ensure `profiles.yml` is set and `dbt debug` passes in `olist/` |