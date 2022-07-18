from typing import Callable, NamedTuple


Url = str
Method = Callable[[], None]

class LogOptions(NamedTuple):
    logger: Callable[[str], None]
    message: str


Logger = Callable[[str], None]
