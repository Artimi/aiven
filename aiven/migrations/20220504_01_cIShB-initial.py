"""
Initial
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
CREATE TABLE pings (
    url VARCHAR NOT NULL, 
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    response_time DOUBLE PRECISION,
    status_code INTEGER,
    content_check BOOLEAN,
    PRIMARY KEY (url, timestamp)
)""",
        """
DROP TABLE pings 
    """,
    )
]
