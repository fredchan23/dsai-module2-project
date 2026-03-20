# BigQuery Ingestion Learning Notes (Session Summary)

## Context

This note captures what we learned and changed during the project setup discussion for Olist ingestion into BigQuery.

## Final Ingestion Strategy

- Dataset selected: Olist (Brazilian E-Commerce)
- Warehouse: BigQuery project `olistdatapipelinebigquery`
- Landing path: `gs://olistdatapipelinebigquery-raw/olist_raw`
- Ingestion approach: GCS -> BigQuery load jobs
- Rule: one BigQuery raw table per Olist entity/schema

Why:
- Team-friendly and reproducible across machines
- Better for shared workflows than local one-off loads
- Works cleanly with dbt raw -> staging -> marts

## Access Setup (Per Member Machine)

Run:

```bash
gcloud auth login
gcloud config set project olistdatapipelinebigquery
gsutil ls gs://olistdatapipelinebigquery-raw/olist_raw
```

If access fails:
- Request access rights from Danny
- Use the same Google account used for GCP login

## Key Loading Rules

- Wildcard loads are safe only when all files have identical schema
- Do not combine different Olist entities into one table
- Keep ingestion as raw loading only (no business logic)

## CLI and Python Patterns

### bq CLI pattern

```bash
bq load --source_format=CSV \
  olistdatapipelinebigquery:raw_olist.<target_table> \
  gs://olistdatapipelinebigquery-raw/olist_raw/<source_file_or_wildcard>.csv
```

### Python pattern (google-cloud-bigquery)

- Use `client.load_table_from_uri(...)`
- Set CSV options (`source_format`, `skip_leading_rows`, `autodetect`)
- Choose write mode by use case (`WRITE_TRUNCATE` for refresh, `WRITE_APPEND` for incremental)

## Big Change in Notebook Workflow

- Reporting workflow no longer depends on creating BigQuery star-schema tables directly from notebooks
- Canonical reporting notebook now focuses on generating dbt artifacts
- This avoids permission blockers such as dataset/table create permissions

## Error We Hit and Lesson

Issue seen:
- `NotFound: Dataset olistdatapipelinebigquery:dw_olist was not found`

Lesson:
- Do not hard-code analysis notebooks to a dataset that may not exist in every member environment
- Use either:
  - dbt-generated models with proper deployment permissions, or
  - fallback queries against raw tables

## Environment Management (Conda)

Project environment file:
- `ds2fgp2.yml`

Current environment name:
- `ds2fgp2`

Use:

```bash
conda env create -f ds2fgp2.yml
conda env update -f ds2fgp2.yml --prune
conda activate ds2fgp2
```

Important:
- If new dependencies are needed, update `ds2fgp2.yml` in the same change/push
- `--prune` removes undeclared packages so env stays reproducible

## Team Ownership Snapshot

- Repo: Brian
- Data ingestion: Danny
- Transformation: All members
- Presentation: All members
- Documentation: All members (Copilot-assisted updates)

## Practical Checklist for Future Sprints

1. Confirm project and GCS access first
2. Validate schema compatibility before wildcard loads
3. Keep ingestion and transformation concerns separate
4. Use dbt for dimensional model materialization
5. Keep environment spec updated and version-pinned
6. Update README progress based on commit evidence
