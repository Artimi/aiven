import dataclasses
import json
import logging
import re
import time

import kafka
import requests

import aiven.settings
import aiven.types


def check_regex(content: str, regex: str) -> bool:
    '''
    Check whether content contains regex.
    '''
    return re.search(regex, content) is not None


def ping_website(url: str, timeout: float, regex: str) -> aiven.types.Ping:
    '''
    Pings `url` under `timeout`. If requests is not completed withing timeout return empty Ping,
    else if request passes it creates Ping from information in response.
    '''
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        logging.getLogger("ping_website").warning(
            "Request to %s, timed out after %s s", url, timeout
        )
        return aiven.types.Ping(
            url=url, response_time=None, status_code=None, content_check=False
        )
    return aiven.types.Ping(
        url=url,
        response_time=response.elapsed.total_seconds(),
        status_code=response.status_code,
        content_check=check_regex(response.text, regex),
    )


def produce() -> None:
    '''
    Run endless loop that calls `ping_website` and send its result to Kafka.
    '''
    logger = logging.getLogger("producer")
    logger.info("Start producing")
    producer = kafka.KafkaProducer(
        bootstrap_servers=aiven.settings.KAFKA_URI,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )
    logger.info("Kafka connected")

    while True:
        ping = ping_website(
            aiven.settings.URL, aiven.settings.CHECK_TIMEOUT, aiven.settings.REGEX
        )
        producer.send("pings", dataclasses.asdict(ping))
        logger.info("Produced: %s", ping)
        time.sleep(aiven.settings.CHECK_PERIOD)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    logging.getLogger("kafka.conn").setLevel(logging.WARNING)
    produce()
