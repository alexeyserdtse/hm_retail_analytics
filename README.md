# hm_retail_analytics

Dimensional warehouse over the [H&M fashion dataset](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) —
dbt on DuckDB, orchestrated with Airflow (in progress). 31.8M transactions across
25 months, modeled as a Kimball star with SCD2 price history.

## Data

The dataset (~3.5 GB, three CSVs) is not in the repo. Download `transactions_train.csv`,
`articles.csv` and `customers.csv` from Kaggle (accept the competition rules first) into
`include/data/raw/`, then convert them once to Parquet:

```bash
python include/scripts/csv_to_parquet.py
```

IDs are kept as text on purpose: `article_id` carries leading zeros and `customer_id`
is a hex string — numeric inference would mangle both.

## Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install dbt-duckdb duckdb pytest sqlfluff sqlfluff-templater-dbt
cd include/hm_dwh && dbt deps && cd ../..
export HM_DB_PATH="$PWD/dev.duckdb"
python -m pytest
```

## Loading

The loader owns the physical `raw.*` tables in `dev.duckdb` (repo root, gitignored).
Dimensions are replaced whole; transactions load month by month with delete+insert,
so any month can be rerun safely. Every attempt is audited in `raw.load_log`.

```bash
python include/scripts/loader.py --history      # dims + all 25 months
python include/scripts/loader.py --month 2019-01
```

## Warehouse

Three layers, `raw → stg → dwh`, each in its own DuckDB schema:

| Layer | What it does | Materialization |
|---|---|---|
| `raw` | source definitions + thin views over the landing tables | view |
| `stg` | rename, cast, clean — 1:1 with raw, no joins | view |
| `dwh` | business-facing star schema | table |

```
dim_customer ─┐               ┌─ dim_article ── snap_article_price (SCD2)
              ├── fct_sales ──┤
dim_date ─────┘               └─ dim_channel
```

`fct_sales` is incremental (delete+insert by month, grain: date × customer ×
article × channel). `snap_article_price` tracks monthly median price per article —
the snapshot reads only the raw layer and only `dim_article` consumes it, which
keeps the dbt graph acyclic. Deliberate modeling calls, from profiling the raw
data: repeat purchase rows are kept and counted into `quantity` (they are real,
not duplicates), and `FN`/`Active` nulls mean "not opted in", not missing.

```bash
cd include/hm_dwh
dbt deps
dbt build          # seeds, snapshot, models, tests — dependency order
dbt build --select stg          # one layer
dbt run --select fct_sales --vars '{month: "2019-01"}'   # rebuild one month
```

Packages: dbt_utils (date spine, surrogate keys), dbt_expectations (distribution
tests), dbt_project_evaluator (structure lint), codegen (yml scaffolding).

## Checks

```bash
python -m pytest                     # loader + converter tests
sqlfluff lint include/hm_dwh/models
```

CI runs the same on every PR: pytest, `dbt parse`, sqlfluff. `master` requires a
green check and a PR — no direct pushes.

## Caveats

- DuckDB allows one writer: close DBeaver (or any client) before running dbt or
  the loader.
- The Kaggle data is competition-licensed; nothing from it is committed here.
- `dim_article.current_price` is null for ~1k articles that never sold.
