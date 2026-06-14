import logging

import duckdb
import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

# Конфигурация DAG
OWNER = "a.khlopkov"
DAG_ID = "raw_from_api_to_s3"

# Используемые таблицы в DAG
LAYER = "raw"
SOURCE = "earthquake"

# S3
ACCESS_KEY = Variable.get("access_key")
SECRET_KEY = Variable.get("secret_key")

LONG_DESCRIPTION = """
# LONG DESCRIPTION
"""

SHORT_DESCRIPTION = "SHORT DESCRIPTION"

args = {
    "owner": OWNER,
    "start_date": pendulum.datetime(2025, 5, 1, tz="Europe/Moscow"),
    "catchup": True,
    "retries": 3,
    "retry_delay": pendulum.duration(hours=1),
}


def get_dates(**context) -> tuple[str, str]:
    """"""
    start_date = context["data_interval_start"].format("YYYY-MM-DD")
    end_date = context["data_interval_end"].format("YYYY-MM-DD")

    return start_date, end_date


def get_and_transfer_api_data_to_s3(**context):
    """"""

    start_date, end_date = get_dates(**context)

    # Добавляем вывод сырых значений переменных в лог
    logging.info(f"Raw start_date: {repr(start_date)}")  # выводит raw string для start_date
    logging.info(f"Raw end_date: {repr(end_date)}")  # выводит raw string для end_date

    logging.info(f"💻 Start load for dates: {start_date}/{end_date}")

    con = duckdb.connect()

    # Тестовый запрос сначала
    test_url = f"https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,relative_humidity_2m,dew_point_2m&timezone=Europe%2FMoscow&format=csv"
    logging.info(f"Test URL: {test_url}")

    con.sql(f"""
            SET TIMEZONE='UTC';
            INSTALL httpfs;
            LOAD httpfs;
            SET s3_url_style = 'path';
            SET s3_endpoint = 'minio:9000';
            SET s3_access_key_id = '{ACCESS_KEY}';
            SET s3_secret_access_key = '{SECRET_KEY}';
            SET s3_use_ssl = FALSE;

            COPY (
                SELECT 
                    *
                    , 52.54833 AS latitude
                    , 13.407822 AS longitude
                    , 38 AS elevation
                    , 'Europe/Moscow' AS timezone
                FROM read_csv_auto('{test_url}', skip=3, normalize_names=True)
            ) TO 's3://prod/{LAYER}/{SOURCE}/{start_date}/{start_date}_00-00-00.gz.parquet';
        """)

    con.close()
    logging.info(f"✅ Success: {start_date}")


with DAG(
    dag_id=DAG_ID,
    schedule_interval="0 5 * * *",
    default_args=args,
    tags=["s3", "raw"],
    description=SHORT_DESCRIPTION,
    concurrency=1,
    max_active_tasks=1,
    max_active_runs=1,
) as dag:
    dag.doc_md = LONG_DESCRIPTION

    start = EmptyOperator(
        task_id="start",
    )

    get_and_transfer_api_data_to_s3 = PythonOperator(
        task_id="get_and_transfer_api_data_to_s3",
        python_callable=get_and_transfer_api_data_to_s3,
    )

    end = EmptyOperator(
        task_id="end",
    )

    start >> get_and_transfer_api_data_to_s3 >> end