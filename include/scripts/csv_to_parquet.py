"""One-time conversion of the Kaggle CSVs to Parquet.

Reads include/data/raw/*.csv, writes include/data/parquet/*.parquet.
Skips files already converted unless --force is given.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


class CsvToParquetConverter:
    # IDs stay text: article_id carries leading zeros, customer_id is a hex string.
    DEFAULT_TYPE_OVERRIDES: dict[str, dict[str, str] | None] = {
        "transactions_train": {"article_id": "VARCHAR", "customer_id": "VARCHAR"},
        "articles": {"article_id": "VARCHAR"},
        "customers": {"customer_id": "VARCHAR"},
    }

    def __init__(
        self,
        data_dir: Path | None = None,
        type_overrides: dict[str, dict[str, str] | None] | None = None,
    ) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
        self.type_overrides = type_overrides or self.DEFAULT_TYPE_OVERRIDES

    def convert(
        self,
        src: Path,
        dst: Path,
        types: dict[str, str] | None = None,
        force: bool = False,
    ) -> int:
        if dst.exists() and not force:
            return 0
        if force:
            dst.unlink(missing_ok=True)
        dst.parent.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect()
        type_arg = f", types={types!r}" if types else ""
        con.execute(
            f"copy (select * from read_csv('{src}'{type_arg})) to '{dst}' (format parquet)"
        )
        return con.sql(f"select count(*) from '{dst}'").fetchone()[0]

    def convert_all(self, force: bool = False) -> None:
        for name, types in self.type_overrides.items():
            src = self.data_dir / "raw" / f"{name}.csv"
            dst = self.data_dir / "parquet" / f"{name}.parquet"
            rows = self.convert(src, dst, types, force=force)
            print(f"{name}: {'skipped (exists)' if rows == 0 else f'{rows:,} rows'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="reconvert even if parquet exists"
    )
    args = parser.parse_args()
    converter = CsvToParquetConverter()
    converter.convert_all(force=args.force)


if __name__ == "__main__":
    main()
