from pathlib import Path

import duckdb

from include.scripts.csv_to_parquet import CsvToParquetConverter


def test_convert_preserves_rows_and_id_strings(tmp_path: Path):
    src = tmp_path / "articles.csv"
    src.write_text("article_id,product_name\n0108775015,Strap top\n0111586001,Shorts\n")
    dst = tmp_path / "articles.parquet"

    converter = CsvToParquetConverter()
    rows = converter.convert(src, dst, types={"article_id": "VARCHAR"})

    assert rows == 2
    out = duckdb.sql(f"select article_id from '{dst}' order by 1").fetchall()
    assert out == [("0108775015",), ("0111586001",)]  # leading zeros intact


def test_convert_skips_existing_without_force(tmp_path: Path):
    src = tmp_path / "a.csv"
    src.write_text("x\n1\n")
    dst = tmp_path / "a.parquet"
    converter = CsvToParquetConverter()
    converter.convert(src, dst, types=None)
    mtime = dst.stat().st_mtime_ns
    converter.convert(src, dst, types=None)  # no force → untouched
    assert dst.stat().st_mtime_ns == mtime
