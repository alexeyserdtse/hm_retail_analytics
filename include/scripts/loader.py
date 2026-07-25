"""Load the Parquet files into physical raw.* tables in DuckDB.

Dimensions are small: full replace. Transactions load month by month,
delete+insert, so any month can be rerun safely. Every attempt lands in
raw.load_log. Airflow calls these same methods in the ingestion DAG.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]


class RawLoader:
    def __init__(self, db_path: Path, parquet_dir: Path):
        self.db_path = db_path
        self.parquet_dir = parquet_dir

    def _connect(self):
        con = duckdb.connect(str(self.db_path))
        con.execute("create schema if not exists raw")
        con.execute("""
            create table if not exists raw.load_log (
                table_name varchar, partition varchar, rows bigint,
                loaded_at timestamp default now(), status varchar
            )
        """)
        return con

    def _validate_name(self, name: str) -> str:
        """Validate dimension table name against whitelist."""
        if name not in ("articles", "customers"):
            raise ValueError(f"Invalid table name: {name}")
        return name

    def load_dimension(self, name: str) -> int:
        name = self._validate_name(name)
        src = self.parquet_dir / f"{name}.parquet"
        con = self._connect()
        try:
            con.execute(f"""
                create or replace table raw.{name} as
                select *, now() at time zone 'utc' as ingestion_ts from '{src}'
            """)
            rows = con.sql(f"select count(*) from raw.{name}").fetchone()[0]
            self._log(con, name, "full", rows)
            return rows
        finally:
            con.close()

    def load_transactions_month(self, month: str) -> int:
        src = self.parquet_dir / "transactions_train.parquet"
        con = self._connect()
        try:
            con.execute("""
                create table if not exists raw.transactions (
                    t_dat date,
                    customer_id varchar,
                    article_id varchar,
                    price double,
                    sales_channel_id integer,
                    ingestion_ts timestamp
                )
            """)
            con.execute("begin")
            try:
                con.execute(
                    "delete from raw.transactions where strftime(t_dat, '%Y-%m') = ?",
                    [month],
                )
                con.execute(
                    f"""
                    insert into raw.transactions
                        (t_dat, customer_id, article_id, price, sales_channel_id, ingestion_ts)
                    select
                        t_dat,
                        customer_id,
                        article_id,
                        price,
                        sales_channel_id,
                        now() at time zone 'utc'
                    from '{src}'
                    where strftime(t_dat, '%Y-%m') = ?
                """,
                    [month],
                )
                con.execute("commit")
                rows = con.sql(
                    "select count(*) from raw.transactions where strftime(t_dat, '%Y-%m') = ?",
                    params=[month],
                ).fetchone()[0]
                self._log(con, "transactions", month, rows)
                return rows
            except Exception:
                try:
                    con.execute("rollback")
                except Exception:
                    pass
                self._log(con, "transactions", month, 0, status="failed")
                raise
        finally:
            con.close()

    def months(self) -> list[str]:
        src = self.parquet_dir / "transactions_train.parquet"
        con = duckdb.connect()
        try:
            return [
                r[0]
                for r in con.sql(
                    f"select distinct strftime(t_dat, '%Y-%m') from '{src}' order by 1"
                ).fetchall()
            ]
        finally:
            con.close()

    def _log(self, con, table: str, partition: str, rows: int, status: str = "ok"):
        con.execute(
            "insert into raw.load_log (table_name, partition, rows, status) values (?, ?, ?, ?)",
            [table, partition, rows, status],
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dims", action="store_true")
    group.add_argument("--month")
    group.add_argument("--history", action="store_true")
    args = parser.parse_args()

    loader = RawLoader(
        REPO_ROOT / "dev.duckdb", REPO_ROOT / "include" / "data" / "parquet"
    )
    if args.dims or args.history:
        for name in ("articles", "customers"):
            print(f"raw.{name}: {loader.load_dimension(name):,} rows")
    if args.month:
        print(
            f"raw.transactions {args.month}: {loader.load_transactions_month(args.month):,} rows"
        )
    if args.history:
        for month in loader.months():
            print(
                f"raw.transactions {month}: {loader.load_transactions_month(month):,} rows"
            )


if __name__ == "__main__":
    main()
