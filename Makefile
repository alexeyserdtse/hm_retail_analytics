VENV := .venv
PY := $(VENV)/bin/python
DBT := cd include/hm_dwh && ../../$(VENV)/bin/dbt
COMPETITION := h-and-m-personalized-fashion-recommendations
RAW := include/data/raw

.PHONY: setup data load build test lint clean help quickstart

quickstart: setup data load build test ## everything: venv, download, load, build, verify

help:
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

setup: ## venv, python deps, dbt packages
	python3.12 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet dbt-duckdb duckdb pytest kaggle sqlfluff sqlfluff-templater-dbt
	$(DBT) deps

data: ## download the three CSVs (needs ~/.kaggle/kaggle.json + accepted rules) and convert to parquet
	mkdir -p $(RAW)
	cd $(RAW) && for f in transactions_train.csv articles.csv customers.csv; do \
		../../../$(VENV)/bin/kaggle competitions download -c $(COMPETITION) -f $$f && \
		unzip -o $$f.zip && rm -f $$f.zip; done
	$(PY) include/scripts/csv_to_parquet.py

load: ## load dims + all 25 months into dev.duckdb
	$(PY) include/scripts/loader.py --history

build: ## dbt build: seeds, snapshot, models, tests
	$(DBT) build

test: ## pytest + sqlfluff
	$(PY) -m pytest -q
	HM_DB_PATH="$$PWD/dev.duckdb" $(VENV)/bin/sqlfluff lint include/hm_dwh

lint: test ## alias

clean: ## drop derived local state (keeps raw csvs)
	rm -rf include/hm_dwh/target include/hm_dwh/logs include/data/parquet dev.duckdb

up: ## start local airflow (astro)
	astro dev start

down: ## stop local airflow
	astro dev stop
