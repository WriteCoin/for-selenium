from abc import ABC, abstractmethod
import traceback
from typing import Callable, Dict, Optional
from typing_extensions import Self
import undetected_chromedriver as uc
from selenium.webdriver.remote.webelement import WebElement

from script import Url

BrowserOptions = Dict[str, str]


class Script(ABC):
    default_thread_number = 0

    def __init__(
        self,
        url: Url,
        thread_number: int = default_thread_number,
        options: BrowserOptions = {},
        load_url: bool = True,
    ) -> None:
        self.url = url
        self.thread_number = thread_number
        self.options = options
        self.load_url = load_url

    def default_driver_options(self):
        options = uc.ChromeOptions()
        for key, value in self.options.items():
            options.add_argument("=".join([key, value]))
        return options

    def default_driver(self):
        return uc.Chrome(options=self.driver_options)

    @staticmethod
    def default_print_error(ex: Exception, viewTrace: bool = True):
        print(ex)
        if viewTrace:
            print(traceback.format_exc())

    def run(
        self,
        driver: Optional[uc.Chrome] = None,
        driver_options: Optional[uc.ChromeOptions] = None,
        printError: Callable[[Exception], None] = default_print_error,
        viewTrace: bool = True,
    ):
        try:
            driver_options = (
                self.default_driver_options()
                if driver_options is None
                else driver_options
            )
            self.driver_options = driver_options
            driver = self.default_driver() if driver is None else driver
            self.driver = driver

            if self.load_url and driver.current_url.startswith(self.url):
                driver.get(self.url)
        except Exception as ex:
            printError(ex)

    def run_with_handle_errors(
        self, driver: Optional[uc.Chrome] = None, driver_options: Optional[uc.ChromeOptions] = None
    ):
        try:
            self.run(driver, driver_options)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())

    def with_treads_run(self):
        pass
        # if self.thread_number <= Script.default_thread_number:

        #   return
        # threadList: list[threading.Thread] = []
        # for i in range(count):
        #   thread = threading.Thread(target=func, args=(i,))
        #   thread.start()
        #   if not name is None:
        #     thread.setName(name)
        #   threadList.append(thread)
        # for thread in threadList:
        #   thread.join()

    def with_threads_and_handle_errors_run(self):
        pass
