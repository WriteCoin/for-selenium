from typing import Callable
import winsound
from numpy import number
from element import By, FindOptions
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

class CantSolveCaptcha(Exception):
  """Error solve captcha"""

def manual_solve_captcha(driver: uc.Chrome, driverOptions: uc.ChromeOptions = None) -> None:
  winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS)
  driver.maximize_window()

DEFAULT_MAX_SOLVE_TIME = 300
DEFAULT_FREQUENCY = 0.5

def solve_captcha(
    driver: uc.Chrome, 
    solveFun: Callable[[uc.Chrome], None],
    condSolve: Callable[[uc.Chrome], bool],
    frame: FindOptions = FindOptions(By.NAME, ""),
    preSolveFun: Callable[[uc.Chrome], None] = None,
    maxSolveTime: float = DEFAULT_MAX_SOLVE_TIME,
    singleCall: bool = False,
    frequency: float = DEFAULT_FREQUENCY,
  ) -> None:
  if (solveFun == manual_solve_captcha):
    singleCall = True
  frame = driver.find_element(frame.by.value, frame.value)
  driver.switch_to.frame(frame)
  if (callable(preSolveFun)):
    preSolveFun(driver)
  def solve_cond(driver: uc.Chrome):
    if (not singleCall):
      solveFun(driver)
    return condSolve(driver)
  if (not condSolve(driver)):
    solveFun(driver)
    WebDriverWait(driver, maxSolveTime, frequency).until(solve_cond)
  if (not condSolve(driver)):
    raise CantSolveCaptcha
  driver.switch_to.default_content()