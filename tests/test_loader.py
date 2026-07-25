from pathlib import Path

import duckdb

from include.scripts.loader import RawLoader


def make_parquet(dir_: Path):
    con = duckdb.connect()
    con.execute(f"""
        copy (select * from (values
            (date '2019-01-05', 'c1', 'a1', 0.05, 1),
            (date '2019-01-06', 'c1', 'a2', 0.10, 2),
            (date '2019-02-01', 'c2', 'a1', 0.05, 2)
        ) t(t_dat, customer_id, article_id, price, sales_channel_id))
        to '{dir_ / "transactions_train.parquet"}' (format parquet)
    """)
    con.execute(f"""
        copy (select * from (values ('a1', 'Top'), ('a2', 'Shorts')) t(article_id, prod_name))
        to '{dir_ / "articles.parquet"}' (format parquet)
    """)


def test_month_load_is_idempotent(tmp_path: Path):
    make_parquet(tmp_path)
    loader = RawLoader(db_path=tmp_path / "t.duckdb", parquet_dir=tmp_path)

    assert loader.load_transactions_month("2019-01") == 2
    assert loader.load_transactions_month("2019-01") == 2  # rerun: replace, not append

    con = duckdb.connect(str(tmp_path / "t.duckdb"))
    assert con.sql("select count(*) from raw.transactions").fetchone()[0] == 2
    assert con.sql("select count(*) from raw.load_log").fetchone()[0] == 2


def test_dimension_full_replace_and_months(tmp_path: Path):
    make_parquet(tmp_path)
    loader = RawLoader(db_path=tmp_path / "t.duckdb", parquet_dir=tmp_path)

    assert loader.load_dimension("articles") == 2
    assert loader.load_dimension("articles") == 2
    assert loader.months() == ["2019-01", "2019-02"]

    con = duckdb.connect(str(tmp_path / "t.duckdb"))
    assert con.sql("select count(*) from raw.articles").fetchone()[0] == 2
    cols = [r[0] for r in con.sql("describe raw.articles").fetchall()]
    assert "ingestion_ts" in cols
