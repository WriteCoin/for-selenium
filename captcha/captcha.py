from typing import Callable, Optional
import winsound
from numpy import number
from undetected_chromedriver.reactor import asyncio
from element import By, FindOptions
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from sound.test import play


class CantSolveCaptcha(Exception):
    """Error solve captcha"""


def manual_solve_captcha(
    driver: uc.Chrome, driverOptions: Optional[uc.ChromeOptions] = None
) -> None:
    asyncio.create_task(play())
    driver.maximize_window()


DEFAULT_MAX_SOLVE_TIME = 300
DEFAULT_FREQUENCY = 0.5


def solve_captcha(
    driver: uc.Chrome,
    solveFun: Callable[[uc.Chrome], None],
    condSolve: Callable[[uc.Chrome], bool],
    frame_op: FindOptions = FindOptions(By.NAME, ""),
    preSolveFun: Optional[Callable[[uc.Chrome], None]] = None,
    maxSolveTime: float = DEFAULT_MAX_SOLVE_TIME,
    singleCall: bool = False,
    frequency: float = DEFAULT_FREQUENCY,
) -> None:
    if solveFun == manual_solve_captcha:
        singleCall = True
    frame = driver.find_element(frame_op.by, frame_op.value)
    driver.switch_to.frame(frame_op)
    if callable(preSolveFun):
        preSolveFun(driver)

    def solve_cond(driver: uc.Chrome):
        if not singleCall:
            solveFun(driver)
        return condSolve(driver)

    if not condSolve(driver):
        solveFun(driver)
        WebDriverWait(driver, maxSolveTime, frequency).until(solve_cond)
    if not condSolve(driver):
        raise CantSolveCaptcha
    driver.switch_to.default_content()
