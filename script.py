from dataclasses import dataclass
from functools import partial
from multiprocessing import Pool
from multiprocessing.dummy import Array, freeze_support
import threading
import traceback
from typing import Callable, Optional, Tuple, TypeAlias, TypeVar
from wsgiref.simple_server import WSGIRequestHandler
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

Url: TypeAlias = str
Method: TypeAlias = Callable[[], None]

def wait_until(driver: uc.Chrome, cond: Callable[[], bool], time: int = 60) -> None:
  WebDriverWait(driver, time).until(lambda driver: cond())

def multiprocessing_start(url: Url, threads: int, func: Callable[[Url], Url | None]):
  urls_list = [url] * threads
  p = Pool(processes=threads)
  p.map(func, urls_list)

def threading_start(count: int, func: Callable[[int], None], name: str = None) -> None:
  if count <= 1:
    func(0)
    return
  threadList: list[threading.Thread] = []
  for i in range(count):
    thread = threading.Thread(target=func, args=(i,))
    thread.start()
    if not name is None:
      thread.setName(name)
    threadList.append(thread)
  for thread in threadList:
    thread.join()

def printError(ex: Exception, dev: bool = True) -> None:
  print(ex)
  if dev:
    print(traceback.format_exc())

def defaultCloseDriver(driver: uc.Chrome) -> None:
  driver.close()
  driver.quit()

def defaultChromeOptions() -> uc.ChromeOptions:
  options = uc.ChromeOptions()
  return options

def defaultChromeGetter(driverOptions: uc.ChromeOptions, freeze: bool = False) -> uc.Chrome:
  if freeze:
    freeze_support()
  return uc.Chrome(options=driverOptions)

def defaultScript(driver: uc.Chrome, driverOptions: uc.ChromeOptions) -> None:
  print("Hello")

def new_chrome_script(
    url: Url,
    loadUrl: bool = True,
    driverOptions: uc.ChromeOptions = None,
    driver: uc.Chrome = None, 
    printExcept: Callable[[Exception], None] = printError,
    script: Callable[[uc.Chrome, uc.ChromeOptions], None] = defaultScript
  ):
  try:
    driverOptions = defaultChromeOptions() if driverOptions is None else driverOptions
    driver = defaultChromeGetter(driverOptions) if driver is None else driver
    if loadUrl and not driver.current_url.startswith(url):
      driver.get(url)
    script(driver, driverOptions)
  except Exception as ex:
    printExcept(ex)

def mapper(url: Url, scriptFunc: Method) -> list[Url]:
  scriptFunc()
  return []

class Script:
  def __init__(self, 
      thread_number: int, 
      url: Url, 
      driver: uc.Chrome | None = None, 
      driver_options: uc.ChromeOptions | None = None,
      options: str = None) -> None:
    freeze_support()
    self.thread_number = thread_number
    self.url = url
    self.driver = driver if driver is not None else uc.Chrome()
    self.driver_options = driver_options if driver_options is not None else uc.ChromeOptions()
    if options is not None:
      optionsList = options.split("\n")
      for option in optionsList:
        self.driver_options.add_argument(option)

  def multiprocessing_start(self, scriptFunc: Method):
    urls_list = [self.url] * self.thread_number
    p = Pool(processes=self.thread_number)
    p.map(partial(mapper, scriptFunc=scriptFunc), urls_list)

  def with_driver(self, callback: Method):
    self.driver.get(self.url)
    try:
      callback()
    except Exception as ex:
      print(ex)
      print(traceback.format_exc())
  
  def test(self, callback: Callable[[str], None]):
    try:
      while True:
        print("Введите для продолжения:")
        string = input()
        callback(string)
    except EOFError:
      print("Завершение работы скрипта")
      self.end()

  def end(self):
    self.driver.close()
    self.driver.quit()

  def with_driver_test(self, callback: Callable[[str], None]):
    self.with_driver(lambda: self.test(callback))
  
  def with_driver_test_default(self, callback: Method):
    self.with_driver_test(lambda string: callback())

def run2():
  print("abc")

def main_script():
  threads = 1
  url = "https://democaptcha.com/demo-form-eng/hcaptcha.html"

  def run():
    print("Мой скрипт")
    driver = script.driver
    textBlock = driver.find_element(By.NAME, "demo_text")
    print(textBlock)

  script = Script(
    thread_number=threads, 
    url=url,
    driver_options="--disable-blink-features=AutomationControlled"
  )
  script.multiprocessing_start(run2)

# def script2(driver: uc.Chrome, driverOptions: uc.ChromeOptions, url: Url):
#   pass

def chromeOptions():
  op = uc.ChromeOptions()
  op.add_argument("--disable-blink-features=AutomationControlled")
  return op

def script_thread(url: Url, loadUrl: bool = True) -> None:
  try:
    driver = uc.Chrome()
    threading.current_thread().join()
    print("Скрипт")
  except Exception as ex:
    print(ex)
    print(traceback.format_exc())
  finally:
    defaultCloseDriver(driver)

def test_script(driver: uc.Chrome, driverOptions: uc.ChromeOptions):
  print("Hello")

def test_script2(driver: uc.Chrome, driverOptions: uc.ChromeOptions, i: int):
  print(f"Hello, номер потока {i}")

def func(i: int):
  url = "https://democaptcha.com/demo-form-eng/hcaptcha.html"
  new_chrome_script(url=url)

def main_script2():

  # multiprocessing_start(url, 1, new_chrome_script)
  # multiprocessing_start(url, 1, partial(new_chrome_script, chromeOptionsGetter=chromeOptions))
  # multiprocessing_start(url, 1, script_thread)

  # partial(lambda i: new_chrome_script(url=url), i=0)()
  # new_chrome_script(url=url)
  # freeze_support()
  threading_start(1, func)

if __name__ == '__main__':
  # main_script()
  # main_script2()
  url = "https://democaptcha.com/demo-form-eng/hcaptcha.html"
  threading_start(1, func)
  # threading_start(1, lambda i: new_chrome_script(url=url, script=lambda driver, driverOptions: print(f"Hello, номер потока {i}")))
  # freeze_support()
  # print(1)