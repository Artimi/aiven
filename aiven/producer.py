from typing import Any
import dataclasses
import json
import logging
import re
import time

import kafka
import requests

import aiven.settings
import aiven.types
import aiven.utils


def check_regex(content: str, regex: str) -> bool:
    """
    Check whether content contains regex.
    """
    return re.search(regex, content) is not None


def ping_website(url: str, timeout: float, regex: str) -> aiven.types.Ping:
    """
    Pings `url` under `timeout`. If requests is not completed withing timeout return empty Ping,
    else if request passes it creates Ping from information in response.
    """
    timestamp = time.time()
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        logging.getLogger("ping_website").warning(
            "Request to %s, timed out after %s s", url, timeout
        )
        return aiven.types.Ping(
            url=url,
            timestamp=timestamp,
            response_time=None,
            status_code=None,
            content_check=False,
        )
    return aiven.types.Ping(
        url=url,
        timestamp=timestamp,
        response_time=response.elapsed.total_seconds(),
        status_code=response.status_code,
        content_check=check_regex(response.text, regex),
    )


def produce(settings: dict[str, Any]) -> None:
    """
    Run endless loop that calls `ping_website` and send its result to Kafka.
    """
    logger = logging.getLogger("producer")
    logger.info("Start producing")
    producer = kafka.KafkaProducer(
        bootstrap_servers=settings["KAFKA_URI"],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )
    logger.info("Kafka connected")

    while True:
        ping_start_time = time.monotonic()
        ping = ping_website(
            settings["URL"], settings["CHECK_TIMEOUT"], settings["REGEX"]
        )
        producer.send(settings["KAFKA_TOPIC"], dataclasses.asdict(ping))
        logger.info("Produced: %s", ping)
        # sleep for the remaining time to ping every CHECK_PERIOD
        time.sleep(
            max(0, ping_start_time + settings["CHECK_PERIOD"] - time.monotonic())
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    logging.getLogger("kafka.conn").setLevel(logging.WARNING)
    produce(aiven.utils.module_to_dict(aiven.settings))
