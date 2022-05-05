import os

URL = "https://aiven.io/"
REGEX = r"simple"
CHECK_PERIOD = 10.0
CHECK_TIMEOUT = 10.0

KAFKA_URI = os.environ["KAFKA_URI"]
KAFKA_TOPIC = "pings"

POSTGRES_URI = os.environ["POSTGRES_URI"]
