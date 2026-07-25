from pathlib import Path

import pytest

# these tests run where airflow exists (astro dev pytest / the ci dags job)
pytest.importorskip("airflow")

from airflow.dag_processing.dagbag import DagBag  # noqa: E402

DAGS_DIR = Path(__file__).resolve().parents[2] / "dags"


def _bag() -> DagBag:
    return DagBag(dag_folder=str(DAGS_DIR))


def test_dags_import_cleanly():
    bag = _bag()
    assert bag.import_errors == {}
    assert len(bag.dags) == 2


def test_dag_hygiene():
    for dag in _bag().dags.values():
        assert dag.default_args.get("retries", 0) >= 1
        assert dag.default_args.get("owner") not in (None, "airflow")
        assert dag.max_active_runs == 1  # duckdb single-writer
