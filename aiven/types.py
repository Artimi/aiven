from typing import Optional
import dataclasses


@dataclasses.dataclass
class Ping:

    url: str
    """URL of the checked page"""

    response_time: Optional[float]
    """Response time in seconds, None if request timed out"""

    status_code: int
    """Response HTTP status code"""

    content_check: bool
    """Whether we found expected regexp on the page"""
