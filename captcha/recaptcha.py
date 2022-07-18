from multiprocessing.dummy import freeze_support
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from typing import Callable
import undetected_chromedriver as uc
import winsound
from selenium.webdriver.remote.webelement import WebElement
# from captcha.captcha import manual_solve_captcha, solve_captcha
# from driver.element import By, FindOptions, switch_through_default
# from driver.script import new_chrome_script, threading_start

DEFAULT_MAX_SOLVE_TIME = 300
DEFAULT_FREQUENCY = 0.5

defaultCheckboxOp = FindOptions(By.ID, "recaptcha-anchor")
defaultCheckboxAttrCond = "aria-checked"


def recaptcha_pre_solve(
    driver: uc.Chrome, checkboxOp: FindOptions = defaultCheckboxOp
) -> None:
    checkbox = driver.find_element(checkboxOp.by.value, checkboxOp.value)
    checkbox.click()
    


defaultFrameOp = FindOptions(By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]')
defaultTaskFrameOp = FindOptions(
    By.CSS_SELECTOR,
    'iframe[title="текущую проверку reCAPTCHA можно пройти в течение ещё двух минут"]',
)
defaultAttrValueCond = "true"


def recaptcha_cond_solve(
    driver: uc.Chrome,
    checkboxOp: FindOptions = defaultCheckboxOp,
    attrCond: str = defaultCheckboxAttrCond,
    attrValueCond: str = defaultAttrValueCond,
) -> bool:
    checkbox = driver.find_element(checkboxOp.by.value, checkboxOp.value)
    return checkbox.get_attribute(attrCond) == attrValueCond


def solve_recaptcha(
    driver: uc.Chrome,
    solveFun: Callable[[uc.Chrome], None],
    frameOp: FindOptions = defaultFrameOp,
    taskFrameOp: FindOptions = defaultTaskFrameOp,
    preSolveFun: Callable[[uc.Chrome], None] = recaptcha_pre_solve,
    condSolve: Callable[[uc.Chrome], bool] = recaptcha_cond_solve,
    maxSolveTime: float = DEFAULT_MAX_SOLVE_TIME,
    singleCall: bool = False,
    frequency: float = DEFAULT_FREQUENCY,
) -> None:
    def solve_fun(driver: uc.Chrome):
        switch_through_default(
            driver, lambda: driver.find_element(taskFrameOp.by.value, taskFrameOp.value)
        )
        solveFun(driver)
        switch_through_default(
            driver, lambda: driver.find_element(frameOp.by.value, frameOp.value)
        )

    return solve_captcha(
        driver,
        solve_fun,
        condSolve,
        frameOp,
        preSolveFun,
        maxSolveTime,
        singleCall,
        frequency,
    )


test_url = "https://www.google.com/recaptcha/api2/demo"


def script(driver: uc.Chrome, driverOptions: uc.ChromeOptions):
    solve_recaptcha(driver, manual_solve_captcha, singleCall=True)
    driver.close()


def thread_start(i):
    new_chrome_script(url=test_url, script=script)


if __name__ == "__main__":
    threading_start(3, thread_start)
    # for i in range(2):
    #   threading_start(1, threads)
