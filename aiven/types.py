from typing import Optional
import dataclasses


@dataclasses.dataclass
class Ping:

    url: str
    """URL of the checked page"""

    response_time: Optional[float]
    """Response time in seconds, None if request timed out"""

    status_code: Optional[int]
    """Response HTTP status code, None if request timed out"""

    content_check: bool
    """Whether we found expected regexp on the page"""
