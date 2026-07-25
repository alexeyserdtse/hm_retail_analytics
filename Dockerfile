FROM astrocrpublic.azurecr.io/runtime:3.3-2

# dbt lives in its own venv so its deps never fight Airflow's
USER root
RUN python -m venv /usr/local/dbt-venv && \
    /usr/local/dbt-venv/bin/pip install --no-cache-dir dbt-duckdb==1.10.1
USER astro

ENV HM_DB_PATH=/usr/local/airflow/dev.duckdb
