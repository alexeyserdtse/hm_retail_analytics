"""Monthly ingestion of the H&M files into raw.* — dims replaced whole,
transactions loaded per data-interval month. Emits the raw asset that
triggers the dbt job."""

from datetime import datetime, timedelta

from airflow.sdk import Asset, dag, task

RAW_HM_ASSET = Asset("duckdb://raw/hm")

DEFAULT_ARGS = {
    "owner": "alexey",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    schedule="@monthly",
    start_date=datetime(2018, 9, 1),
    end_date=datetime(2020, 10, 1),
    catchup=True,
    max_active_runs=1,  # duckdb allows one writer
    default_args=DEFAULT_ARGS,
    tags=["ingestion"],
)
def hm_ingestion():
    @task
    def load_articles() -> int:
        from include.scripts.loader import REPO_ROOT, RawLoader

        loader = RawLoader(
            REPO_ROOT / "dev.duckdb", REPO_ROOT / "include" / "data" / "parquet"
        )
        return loader.load_dimension("articles")

    @task
    def load_customers() -> int:
        from include.scripts.loader import REPO_ROOT, RawLoader

        loader = RawLoader(
            REPO_ROOT / "dev.duckdb", REPO_ROOT / "include" / "data" / "parquet"
        )
        return loader.load_dimension("customers")

    @task(outlets=[RAW_HM_ASSET])
    def load_transactions(data_interval_start=None) -> int:
        from include.scripts.loader import REPO_ROOT, RawLoader

        loader = RawLoader(
            REPO_ROOT / "dev.duckdb", REPO_ROOT / "include" / "data" / "parquet"
        )
        return loader.load_transactions_month(data_interval_start.strftime("%Y-%m"))

    [load_articles(), load_customers()] >> load_transactions()


hm_ingestion()
