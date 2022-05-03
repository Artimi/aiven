import pytest
import requests
import responses

import aiven.producer

URL = "http://example.com"


@pytest.mark.parametrize(
    "content,regex,should_match",
    [("it is simple", r"simple", True), ("absurdly hard", r"simple", False)],
)
def test_check_regex(content: str, regex: str, should_match: bool) -> None:
    assert aiven.producer.check_regex(content, regex) is should_match


@responses.activate
def test_ping_website_good() -> None:
    responses.add(responses.GET, URL, body="This is simple", status=200)
    ping = aiven.producer.ping_website(URL, 1.0, r"simple")
    assert ping.url == URL
    assert ping.status_code == 200
    assert ping.response_time < 1.0
    assert ping.content_check is True


@responses.activate
def test_ping_website_regex_not_found() -> None:
    responses.add(responses.GET, URL, body="This is absurdly hard", status=200)
    ping = aiven.producer.ping_website(URL, 1.0, r"simple")
    assert ping.url == URL
    assert ping.status_code == 200
    assert ping.response_time < 1.0
    assert ping.content_check is False


@responses.activate
def test_ping_website_timeout() -> None:
    responses.add_callback(responses.GET, URL, callback=requests.exceptions.Timeout)
    ping = aiven.producer.ping_website(URL, 1.0, r"simple")
    assert ping.url == URL
    assert ping.status_code is None
    assert ping.response_time is None
    assert ping.content_check is False
