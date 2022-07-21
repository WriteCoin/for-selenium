import pickle
import time
from contextlib import contextmanager
from typing import Callable, List, Literal, NamedTuple, Optional, Union

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome
from undetected_chromedriver.dprocess import traceback


class FindOptions(NamedTuple):
    by: str
    value: str

class Script:
    default_time_sleep_on_load = 5
    DEFAULT_TIMEOUT = 60.00
    DEFAULT_POLL_FREQUENCY = 0.1

    def __init__(
        self,
        url: str,
        load_url: bool = True,
        cookie_path: Optional[str] = None,
        driver: Optional[Chrome] = None,
        max_error_count: int = 100,
        disable_log: bool = False,
    ) -> None:
        self.url = url
        self.load_url = load_url
        self.cookie_path = cookie_path
        self.driver = driver
        self.cookie_not_found = False
        self.max_error_count = max_error_count
        self.disable_log = disable_log
        self.error_count = 0

        self.log("Бразуер инициализирован")
        self.log(f"URL: {url}")
        self.log(f"Путь к куки: {cookie_path}")
        self.log(f"Предварительная загрузка страницы: {load_url}")
        self.log(f"Макс. кол-во ошибок: {max_error_count}")

    def log(self, message: str):
        if not self.disable_log:
            print(message)

    def driver_check(self, message: str = "No driver"):
        if self.driver is None:
            raise Exception(message)

    def sleep(self, time: Union[int, float]):
        self.driver_check()
        try:
            WebDriverWait(self.driver, float(time), float(time)).until(
                lambda driver: False
            )
        except:
            pass

    def find_element(
        self, element_options: FindOptions, element: Optional[WebElement] = None
    ) -> WebElement:
        if self.driver is None:
            raise Exception("No driver")
        if element is None:
            return self.driver.find_element(element_options.by, element_options.value)
        else:
            return element.find_element(element_options.by, element_options.value)

    def find_elements(
        self, element_options: FindOptions, element: Optional[WebElement] = None
    ) -> List[WebElement]:
        if self.driver is None:
            raise Exception("No driver")
        if element is None:
            return self.driver.find_elements(element_options.by, element_options.value)
        else:
            return element.find_elements(element_options.by, element_options.value)

    def wait_page_load(self, timeout: float = DEFAULT_TIMEOUT):
        if self.driver is None:
            raise Exception("No driver")

        def cond():
            if self.driver is None:
                raise Exception("No driver")
            return self.driver.execute_script(
                """return document.readyState === 'complete'"""
            )

        WebDriverWait(self.driver, timeout).until(cond)

    def is_element_exists(
        self, element_options: FindOptions, element: Optional[WebElement] = None
    ) -> bool:
        if self.driver is None:
            raise Exception("No driver")

        try:
            self.find_element(element_options, element)
        except NoSuchElementException:
            return False
        else:
            return True

    def is_elements_exists(
        self, element_options: FindOptions, element: Optional[WebElement] = None
    ) -> bool:
        return self.find_elements(element_options, element) != []

    def wait_element(
        self,
        element_options: FindOptions,
        timeout: float = DEFAULT_TIMEOUT,
        poll_frequency: float = DEFAULT_POLL_FREQUENCY,
        element: Optional[WebElement] = None,
    ) -> WebElement:
        if self.driver is None:
            raise Exception("No driver")

        def cond(driver: Chrome):
            return self.is_element_exists(element_options, element)

        WebDriverWait(self.driver, timeout, poll_frequency).until(cond)

        return self.find_element(element_options, element)

    def wait_elements(
        self,
        element_options: FindOptions,
        timeout: float = DEFAULT_TIMEOUT,
        poll_frequency: float = DEFAULT_POLL_FREQUENCY,
        element: Optional[WebElement] = None,
    ) -> List[WebElement]:
        if self.driver is None:
            raise Exception("No driver")

        def cond(driver: Chrome):
            return self.is_elements_exists(element_options, element)

        WebDriverWait(self.driver, timeout, poll_frequency).until(cond)

        return self.find_elements(element_options, element)

    def load_cookie(self, time_sleep: int = default_time_sleep_on_load):
        self.log("Загрузка куки")
        if self.driver is None or self.cookie_path is None:
            raise Exception("Загрузка куки невозможна, браузер отсутствует")
        driver = self.driver
        for cookie in pickle.load(open(self.cookie_path, "rb")):
            driver.add_cookie(cookie)
        if time_sleep > 0:
            driver.implicitly_wait(time_sleep)
        driver.refresh()

    def save_cookie(self):
        self.log("Сохранение куки")
        if self.driver is None or self.cookie_path is None:
            raise Exception("Сохранение куки невозможно, браузер отсутствует")
        pickle.dump(self.driver.get_cookies(), open(self.cookie_path, "wb"))

    @contextmanager
    def work_cookie(self):
        """
        Attempt to download cookies. Returns a generator with false if cookies are found, otherwise true
        Попытка загрузить куки. Возвращает генератор с False, если куки были найдены, в противном случае True
        """
        try:
            self.load_cookie()
            yield
        except FileNotFoundError:
            print("Куки не загрузились. Файл не был найден.")
            self.cookie_not_found = True
            yield
        finally:
            self.save_cookie()

    def close_tabs(self, excluded_windows: List[str] = []):
        self.log("Закрытие вкладок браузера:")
        if self.driver is None:
            raise Exception("Закрытие вкладок невозможно, браузер не найден")
        windows = [
            window
            for window in self.driver.window_handles
            if window not in excluded_windows
        ]
        current_window = self.driver.current_window_handle
        all_tabs_closed = True
        for window in windows:
            try:
                self.driver.switch_to.window(window)
                self.driver.close()
            except:
                all_tabs_closed = False
        if all_tabs_closed:
            self.log("Все вкладки браузера закрыты")
        if current_window not in excluded_windows:
            self.driver.switch_to.window(current_window)
            self.log("Браузер переключен на текущую вкладку")

    @contextmanager
    def start(self):
        while self.error_count < self.max_error_count:
            self.log(f"Старт скрипта. Попытка № {self.error_count}")
            if self.driver is None:
                self.driver = Chrome()
            original_window_handle = self.driver.current_window_handle
            window_handles = self.driver.window_handles
            try:
                if self.load_url and not self.driver.current_url.startswith(self.url):
                    self.driver.get(self.url)
                if self.cookie_path is not None:
                    with self.work_cookie():
                        yield original_window_handle
                yield original_window_handle
            except Exception as ex:
                print("Ошибка скрипта", ex)
                print(traceback.format_exc())
                self.close_tabs(window_handles)
                self.error_count += 1
            else:
                break
        if self.driver is not None:
            self.log("Закрытие бразуера")
            self.driver.quit()
            self.log("Закрытие браузера произошло успешно")
        else:
            self.log("Браузер уже закрыт")

    def find_window(
        self, cond: Callable[[str], bool]
    ) -> Union[Union[List[str], None], None]:
        if self.driver is None:
            raise Exception("No driver")
        driver = self.driver
        current_window = driver.current_window_handle
        window_list = []
        for window in driver.window_handles:
            driver.switch_to.window(window)
            if cond(window):
                window_list.append(window)
        driver.switch_to.window(current_window)
        return window_list

    @contextmanager
    def work_tab(self, tab: Union[str, int], multi_tabs: bool = False):
        self.log(f"Работа со вкладкой по аргументу: {tab}")
        if self.driver is None:
            raise Exception("Браузер отсутствует. Работать со вкладкой невозможно")
        driver = self.driver
        current_window = driver.current_window_handle
        try:
            if isinstance(tab, int):
                target_window = driver.window_handles[tab]
            else:
                target_window = None
        except:
            pass
        else:
            if target_window is not None:
                self.log(f"Работа с одним окном: {target_window}")
                driver.switch_to.window(target_window)
                yield target_window
                driver.switch_to.window(current_window)
                return

        windows = self.find_window(lambda window: window == tab)
        if windows is None:
            self.log("Нет необходимых окон, завершение функции")
            return

        def one_or_more(windows: List[str]):
            current_window = driver.current_window_handle
            if len(windows) > 0:
                if len(windows) == 1 or not multi_tabs:
                    target_window = windows[0]
                    self.log(f"Работа с одним окном: {target_window}")
                    driver.switch_to.window(target_window)
                    yield target_window
                else:
                    current_window = driver.current_window_handle
                    self.log(f"Работа с окнами: {windows}")
                    for window in windows:
                        driver.switch_to.window(window)
                        yield window
                driver.switch_to.window(current_window)
            else:
                return False

        flag_none = one_or_more(windows)

        if flag_none == False:

            def cond(window: str):
                if self.driver is not None:
                    return self.driver.current_url == tab
                return False

            windows = self.find_window(cond)
            if windows is None:
                self.log("Нет необходимых окон, завершение функции")
                return
            one_or_more(windows)

    def work_frame(
        self,
        target: WebElement,
        source: Union[Optional[WebElement], Literal["parent"]] = None,
    ):
        if self.driver is None:
            raise Exception("No driver")
        target_html = target.get_attribute("outerHTML")
        self.log(f"Работа с фреймом: {target_html}")
        if source is None:
            self.log("Перемещение из исходной страницы")
        elif source == "parent":
            self.log("Перемещение из родительского фрейма")
        else:
            source_html = source.get_attribute("outerHTML")
            self.log(f"Перемещение из фрейма: {source_html}")
        driver = self.driver

        def to_source():
            if source is None:
                driver.switch_to.default_content()
            elif source == "parent":
                driver.switch_to.parent_frame()
            else:
                driver.switch_to.frame(source)

        to_source()
        driver.switch_to.frame(target)
        yield
        to_source()

        self.log(f"Работа с фреймом: {target_html} успешно завершена")


class TabInfo:
    def __init__(self, script: Script, window_handle: Optional[str] = None) -> None:
        if script.driver is None:
            raise Exception("No driver")
        driver = script.driver
        if window_handle is not None:
            self.handle = window_handle
        else:
            self.handle = driver.current_window_handle
        self.index = script.driver.window_handles.index(self.handle)
        if self.handle != driver.current_window_handle:
            with script.work_tab(self.handle):
                self.title = driver.title
                self.url = driver.current_url
        else:
            self.title = driver.title


if __name__ == "__main__":
    # script = TestScript("https://google.com")

    script = Script("https://yandex.ru")
    with script.start():
        t0 = time.time()
        print("Это скрипт")
        script.sleep(1.25)
        print("Ожидание завершено")
        t1 = time.time()
        print(f"time: {t1 - t0}")
    # time.sleep(5.0)
