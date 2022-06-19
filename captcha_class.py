from abc import ABC, abstractmethod
from element import FindOptions

class Captcha(ABC):
  """Интерфейс любой капчи"""
  def __init__(self, frame_op: FindOptions | None) -> None:
    self._frame_op = frame_op

  @abstractmethod
  def solve(self) -> None:
    pass

class TextCaptcha(Captcha):
  """Интерфейс текстовой капчи"""
  pass

class GraphicCaptcha(Captcha):
  """Интерфейс графической капчи"""
  pass


def captcha_solve():
  pass