import dataclasses
import json
import logging

import kafka

import aiven.settings
import aiven.types


def produce():
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

    ping = aiven.types.Ping(
        url="", response_time=1.0, status_code=200, content_check=True
    )

    producer.send("pings", dataclasses.asdict(ping))
    logger.info("Send %s to kafka", ping)
    producer.flush()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    logging.getLogger("kafka.conn").setLevel(logging.WARNING)
    produce()
