"""Runs the whole dbt project as one job — the DbtCloudRunJobOperator
pattern on dbt Core: Airflow triggers, dbt owns the DAG inside."""

from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import Asset, dag

DBT = "/usr/local/dbt-venv/bin/dbt"
PROJECT = "/usr/local/airflow/include/hm_dwh"

DEFAULT_ARGS = {
    "owner": "alexey",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    schedule=[Asset("duckdb://raw/hm")],
    start_date=datetime(2018, 9, 1),
    catchup=False,
    max_active_runs=1,  # duckdb allows one writer
    default_args=DEFAULT_ARGS,
    tags=["dbt"],
)
def dbt_job():
    build = BashOperator(
        task_id="dbt_build",
        bash_command=f"{DBT} build --project-dir {PROJECT} --profiles-dir {PROJECT}",
    )
    freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"{DBT} source freshness --project-dir {PROJECT} --profiles-dir {PROJECT}",
    )
    build >> freshness


dbt_job()
