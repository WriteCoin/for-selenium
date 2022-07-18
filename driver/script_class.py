from contextlib import contextmanager
from typing import Callable, List, Optional, Union
from undetected_chromedriver import Chrome
from undetected_chromedriver.dprocess import traceback


class Script:
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

    def load_cookie(self):
        pass

    def save_cookie(self):
        pass

    @contextmanager
    def work_cookie(self):
        """
        Attempt to download cookies. Returns a generator with false if cookies are found, otherwise true
        Попытка загрузить куки. Возвращает генератор с False, если куки были найдены, в противном случае True
        """
        try:
            self.load_cookie()
            yield False
        except FileNotFoundError:
            yield True
        finally:
            self.save_cookie()

    def close_tabs(self, excluded_windows: List[str] = []):
        self.log("Закрытие вкладок браузера:")
        if self.driver is not None:
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
        else:
            self.log("Браузера нет, закрытие вкладок невозможно")

    @contextmanager
    def start(self):
        while self.error_count < self.max_error_count:
            self.log(f"Старт скрипта. Попытка № {self.error_count}")
            if self.driver is None:
                self.driver = Chrome()
                self.log("Бразуер новый")
            else:
                self.log("Браузер старый")
                self.driver.t
            original_window_handle = self.driver.current_window_handle
            window_handles = self.driver.window_handles
            try:
                with self.work_cookie():
                    pass
                if self.load_url and not self.driver.current_url.startswith(self.url):
                    self.driver.get(self.url)
                if self.cookie_path is not None:
                    with self.work_cookie() as not_found:
                        yield (not_found, original_window_handle)
                yield (True, original_window_handle)
            except Exception as ex:
                print("Ошибка скрипта", ex)
                print(traceback.format_exc())
                self.close_tabs()
                for window in self.driver.window_handles:
                    if window != original_window_handle:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                self.error_count += 1
            else:
                break
        self.log("Закрытие бразуера")
        if self.driver is not None:
            self.driver.quit()
            self.log("Закрытие браузера произошло успешно")
        else:
            self.log("Закрытие браузера произошло неуспешно")

    def find_window(self, cond: Callable[[str], bool]) -> Union[List[str], None]:
        if self.driver is None:
            return
        driver = self.driver
        current_window = driver.current_window_handle
        window_list = []
        for window in driver.window_handles:
            driver.switch_to.window(window)
            if cond(window):
                window_list.append(window)
        driver.switch_to.window(current_window)
        return window_list

    def work_tab(self, tab: Union[str, int], multi_tabs: bool = False):
        self.log(f"Работа со вкладкой по аргументу: {tab}")
        if self.driver is None:
            self.log("Браузер отсутствует. Работать со вкладкой невозможно")
            return
        driver = self.driver
        current_window = driver.current_window_handle
        try:
            if isinstance(tab, int):
                target_window = driver.window_handles[tab]
                self.log(f"Работа с одним окном: {target_window}")
                driver.switch_to.window(target_window)
                yield target_window
                driver.switch_to.window(current_window)
                return
        except:
            pass

        windows = self.find_window(lambda window: window == tab)
        if windows is None:
            self.log("Нет окон, завершение функции")
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
                self.log("Нет окон, завершение функции")
                return
            one_or_more(windows)


class TabInfo:
    def __init__(self, script: Script, window_handle: Optional[str] = None) -> None:
        if script.driver is not None:
            driver = script.driver
            self.handle = (
                window_handle
                if window_handle is not None
                else driver.current_window_handle
            )
            self.index = script.driver.window_handles.index(self.handle)
            if self.handle != driver.current_window_handle:
                current_handle = driver.current_window_handle
                driver.switch_to.window(self.handle)
                self.title = driver.title
                driver.switch_to.window(current_handle)
            else:
                self.title = driver.title

        else:
            script.log("Браузер отсутствует. Информацию о вкладке получить невозможно")


if __name__ == "__main__":
    script = Script("https://google.com")
    script.close_tabs()
