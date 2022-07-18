from dataclasses import dataclass
from enum import Enum
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from typing import Callable, NamedTuple
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement


@dataclass(frozen=True)
class FindOptions:
    by: str
    value: str


def switch_through_default(driver: uc.Chrome, frameGet: Callable[[], WebElement]):
    driver.switch_to.default_content()
    frame = frameGet()
    driver.switch_to.frame(frame)

if __name__ == '__main__':
    loc = FindOptions(By.CLASS_NAME, "captcha")
    print(loc.by)