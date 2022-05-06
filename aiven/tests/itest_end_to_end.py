from typing import Any, Optional
import datetime
import os
import multiprocessing

import psycopg

import aiven.consumer
import aiven.producer
import aiven.settings
import aiven.utils


POSTGRES_URI = os.environ["POSTGRES_URI"]


def run_and_fetch_pings(
    settings: dict[str, Any], start_time: datetime.datetime
) -> list[tuple[str, datetime.datetime, Optional[float], Optional[int], bool]]:

    producer = multiprocessing.Process(target=aiven.producer.produce, args=(settings,))
    consumer = multiprocessing.Process(target=aiven.consumer.consume, args=(settings,))
    try:
        producer.start()
        consumer.start()
        producer.join(timeout=15)
        consumer.join(timeout=1)
    finally:
        producer.terminate()
        consumer.terminate()

    with psycopg.connect(settings["POSTGRES_URI"], autocommit=True) as db_connection:
        pings = db_connection.execute(
            "SELECT * FROM pings WHERE timestamp > %s", (start_time,)
        ).fetchall()
    return pings


def test_end_to_end() -> None:
    settings = aiven.utils.module_to_dict(aiven.settings)
    start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    pings = run_and_fetch_pings(settings, start_time)
    assert len(pings) >= 1
    url, timestamp, response_time, status_code, content_check = pings[0]
    assert url == settings["URL"]
    assert timestamp > start_time
    assert isinstance(response_time, float)
    assert status_code == 200
    assert content_check
