# hm_retail_analytics

Dimensional warehouse over the [H&M fashion dataset](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations) —
dbt on DuckDB, orchestrated with Airflow. Work in progress.

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
pip install dbt-duckdb duckdb pytest
python -m pytest
```
