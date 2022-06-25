from email import message
import pickle
from time import sleep
from typing import Callable, NamedTuple
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from typtupoi import Url, LogOptions

defaultLoadLogOp = LogOptions(logger=print, message="Загрузка куки")
defaultSaveLogOp = LogOptions(logger=print, message="Сохранение куки")
defaultTimeSleepOnLoad = 5.00

def load_cookie(
  filepath: Url,
  driver: uc.Chrome,
  logOp: LogOptions = defaultLoadLogOp,
  timeSleep: float = defaultTimeSleepOnLoad
) -> None:
  logOp.logger(logOp.message)
  # вариант с pickle из урока
  for cookie in pickle.load(open(filepath, "rb")):
    driver.add_cookie(cookie)
  sleep(timeSleep)
  driver.refresh()

def save_cookie(
  filepath: Url,
  driver: uc.Chrome,
  logOp: LogOptions = defaultSaveLogOp 
) -> None:
  logOp.logger(logOp.message)
  # вариант с pickle из урока
  pickle.dump(driver.get_cookies(), open(filepath, "wb"))

def defaultCallback(cookieNotFound: bool) -> None:
  print("Работа с куки")
  if cookieNotFound:
    print("куки не найдено")

def work_cookie(
  filepath: Url,
  driver: uc.Chrome,
  loadLogOp: LogOptions = defaultLoadLogOp,
  saveLogOp: LogOptions = defaultSaveLogOp,
  timeSleepOnLoad: float = defaultTimeSleepOnLoad,
  callback: Callable[[bool], None] = defaultCallback
):
  cookieNotFound = False
  try:
    load_cookie(filepath, driver, loadLogOp, timeSleepOnLoad)
  except FileNotFoundError as ex:
    cookieNotFound = True
  callback(cookieNotFound)
  save_cookie(filepath, driver, saveLogOp)