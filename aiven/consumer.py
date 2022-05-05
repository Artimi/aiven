import dataclasses
import datetime
import json
import logging

import kafka
import psycopg

import aiven.settings
import aiven.types

STORE_QUERY = """
INSERT INTO pings (url, timestamp, response_time, status_code, content_check)
VALUES (%(url)s, %(timestamp)s, %(response_time)s, %(status_code)s, %(content_check)s)
"""

KAFKA_GROUP = "db_storage"


def store(db_connection: psycopg.Connection, ping: aiven.types.Ping) -> None:
    """
    Store `ping` using `db_connection`. In case of failure log the error.
    """
    logger = logging.getLogger("store")
    ping_dict = dataclasses.asdict(ping)
    ping_dict["timestamp"] = datetime.datetime.fromtimestamp(
        ping_dict["timestamp"], tz=datetime.timezone.utc
    )
    try:
        db_connection.execute(STORE_QUERY, ping_dict)
    except psycopg.errors.Error:
        logger.exception(
            "Storing %s failed. Item was not stored into a database", ping_dict
        )
    logger.info("Stored: %s", ping_dict)


def consume() -> None:
    """
    Connect to kafka, to postgres, consume pings from kafka and store them.
    """
    logger = logging.getLogger("producer")
    logger.info("Start consuming")

    consumer = kafka.KafkaConsumer(
        aiven.settings.KAFKA_TOPIC,
        # be a part of a group so no message will be unprocessed
        group_id=KAFKA_GROUP,
        # we will handle commits by ourselves to not consume already stored messages
        enable_auto_commit=False,
        bootstrap_servers=aiven.settings.KAFKA_URI,
        value_deserializer=lambda v: aiven.types.Ping(**json.loads(v.decode("utf-8"))),
        security_protocol="SSL",
        ssl_cafile="ca.pem",
        ssl_certfile="service.cert",
        ssl_keyfile="service.key",
    )
    logger.info("Kafka connected")

    with psycopg.connect(aiven.settings.POSTGRES_URI, autocommit=True) as db_connection:
        logger.info("Postgres connected")
        for message in consumer:
            logger.debug("Consumed: %s", message)
            store(db_connection, message.value)
            # commit after each message, it isn't problem in low volume
            consumer.commit()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    logging.getLogger("kafka").setLevel(logging.WARNING)
    consume()
