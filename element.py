from enum import Enum
from typing import Callable, NamedTuple, TypeAlias, TypeVar
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement

class By(Enum):
  """
  Set of supported locator strategies.
  """
  ID = "id"
  XPATH = "xpath"
  LINK_TEXT = "link text"
  PARTIAL_LINK_TEXT = "partial link text"
  NAME = "name"
  TAG_NAME = "tag name"
  CLASS_NAME = "class name"
  CSS_SELECTOR = "css selector"

FindValue: TypeAlias = str

class FindOptions(NamedTuple):
  by: By
  value: FindValue

def switch_through_default(driver: uc.Chrome, frameGet: Callable[[], WebElement]):
  driver.switch_to.default_content()
  frame = frameGet()
  driver.switch_to.frame(frame)