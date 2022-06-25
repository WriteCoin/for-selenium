from typing import Callable, NamedTuple, TypeAlias


Url: TypeAlias = str
Method: TypeAlias = Callable[[], None]

class LogOptions(NamedTuple):
  logger: Callable[[str], None]
  message: str

Logger: TypeAlias = Callable[[str], None]