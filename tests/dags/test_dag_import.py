from pathlib import Path

from airflow.models.dagbag import DagBag

DAGS_DIR = Path(__file__).resolve().parents[2] / "dags"


def test_dags_import_cleanly():
    bag = DagBag(dag_folder=str(DAGS_DIR), include_examples=False)
    assert bag.import_errors == {}
    assert len(bag.dags) == 2


def test_dag_hygiene():
    bag = DagBag(dag_folder=str(DAGS_DIR), include_examples=False)
    for dag in bag.dags.values():
        assert dag.default_args.get("retries", 0) >= 1
        assert dag.default_args.get("owner") not in (None, "airflow")
        assert dag.max_active_runs == 1  # duckdb single-writer
