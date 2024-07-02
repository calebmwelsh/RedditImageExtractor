# selenium imports
import os

# other imports
import time

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote import webelement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# set options
OPTIONS = webdriver.ChromeOptions()


class ParserManager:
    """
    Purpose - A web parser object that uses selenium to guide certain web element behaviors
    """

    def __init__(
        self,
        reg_args=[],
        exp_args=[],
        script_exes=[],
        cpd_cmds=[],
        window_size=[1600, 2000],
        current_url: str = None,
    ) -> None:
        # current url
        self.current_url = current_url
        # add options
        self.add_reg_args(reg_args)
        self.add_exp_args(exp_args)
        # web driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=OPTIONS
        )
        # web default wait obj
        self.wait = WebDriverWait(self.driver, 10)
        # add script exes
        self.add_script_exes(script_exes)
        # add cpd cmds
        self.add_cpd_cmds(cpd_cmds)
        # set web driver to url
        if self.current_url:
            self.set_page(self.current_url)
        # set window size
        self.driver.set_window_size(window_size[0], window_size[1])

    """ ------------------------------------------ General Methods ------------------------------------------------ """

    def set_page(self, new_link: str) -> None:
        """
        Purpose - Sets the drivers html site

        Param - new_link: The new link that the driver will be set to
        """
        self.link = new_link
        self.driver.get(self.link)

    def hard_reset(self):
        """
        Purpose - Hard reset page
        """
        # hard reset prompt
        print("\nReseting......")
        # dispose driver
        self.driver.quit()
        # reassign driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=OPTIONS
        )
        # set web driver to url
        self.set_page(self.current_url)

    def refresh_page(self) -> None:
        """
        Purpose - Refreshes the page based on the current link
        """
        self.driver.get(self.link)

    def add_reg_args(self, reg_args: list) -> None:
        """
        Purpose - Adds an arguement to the option object

        Param - reg_args: A list of args that will be added to the webdriver
        """
        for reg_arg in reg_args:
            OPTIONS.add_argument(reg_arg)

    def add_exp_args(self, exp_args: str) -> None:
        """
        Purpose - Adds an experimental arguement to the option object

        Param - exp_args: A list of exp_args that will be added to the webdriver
        """
        for key, value in exp_args.items():
            OPTIONS.add_experimental_option(key, value)

    def add_script_exes(self, script_exes=str) -> None:
        """
        Purpose - Adds an script exe to driver

        Param - script_exes: A list of script_exes that will be added to the webdriver
        """
        for script_exe in script_exes:
            self.driver.execute_script(script_exe)

    def add_cpd_cmds(self, cpd_cmds=str) -> None:
        """
        Purpose - Adds cpd cmds to driver

        Param - cpd_cmds: A list of cpd_cmds that will be added to the webdriver
        """
        for key, value in cpd_cmds.items():
            self.driver.execute_cdp_cmd(key, value)

    """ ------------------------------------------ Locator Methods ------------------------------------------------ """

    def find_element_by_name(self, name: str) -> webelement:
        """
        Purpose - Finds an element by the name locator

        Param - name: The name that is used to search for element
        """
        return self.driver.find_element(By.NAME, name)

    def find_element_by_xpath(self, xpath: str) -> webelement:
        """
        Purpose - Finds an element by the xpath locator

        Param - name: The xpath that is used to search for element
        """
        return self.driver.find_element(By.XPATH, xpath)

    def find_element_by_id(self, element_id: str) -> webelement:
        """
        Purpose - Finds an element by the id locator

        Param - name: The id that is used to search for element
        """
        return self.driver.find_element(By.ID, element_id)

    def find_element_by_class(self, class_name: str) -> webelement:
        """
        Purpose - Finds an element by the class name locator

        Param - name: The class name that is used to search for element
        """
        return self.driver.find_element(By.CLASS_NAME, class_name)

    def find_element_by_tag(self, tag_name: str) -> webelement:
        """
        Purpose - Finds an element by the tag name locator

        Param - name: The tag name that is used to search for element
        """
        return self.driver.find_element(By.TAG_NAME, tag_name)

    def find_element_by_css(self, css_selector: str) -> webelement:
        """
        Purpose - Finds an element by the css selector locator

        Param - name: The css selector that is used to search for element
        """
        return self.driver.find_element(By.CSS_SELECTOR, css_selector)

    def find_link_by_text(self, link_text: str) -> webelement:
        """
        Purpose - Finds an element by the link text locator

        Param - name: The link text that is used to search for element
        """
        return self.driver.find_element(By.LINK_TEXT, link_text)

    """ ------------------------------------------ Wait Methods ------------------------------------------------ """

    def wait_for_element(
        self, search_type: str, search_str: str, element=None, timer: int = 7
    ) -> webelement:
        """
        Purpose - Waits until an element is available

        Param - search_type: The locator that is used to search for element

        Param - search_str: The string that is used to search for element

        Param - element: The element that is used to search for another element (acts as driver)

        Param - timer: The amount of time the driver will wait for an element
        """
        try:
            # if search locator is an element and not the driver
            if element:
                return WebDriverWait(element, timer).until(
                    EC.presence_of_element_located((search_type, search_str))
                )
            # if search locator is the driver and not an element
            else:
                return WebDriverWait(self.driver, timer).until(
                    EC.presence_of_element_located((search_type, search_str))
                )
        # handle timeout
        except TimeoutException as e:
            return False

    def wait_for_elements(
        self, search_type: str, search_str: str, element=None, timer: int = 7
    ) -> webelement:
        """
        Purpose - Waits until an element is available

        Param - search_type: The locator that is used to search for element

        Param - search_str: The string that is used to search for element

        Param - element: The element that is used to search for another element (acts as driver)

        Param - timer: The amount of time the driver will wait for an element
        """
        try:
            # if search locator is an element and not the driver
            if element:
                return WebDriverWait(element, timer).until(
                    EC.presence_of_all_elements_located((search_type, search_str))
                )
            # if search locator is the driver and not an element
            else:
                return WebDriverWait(self.driver, timer).until(
                    EC.presence_of_all_elements_located((search_type, search_str))
                )
        # handle timeout and "The custom error module does not recognize this error."
        except TimeoutException as e:
            return False

    """ ------------------------------------------ Click Methods ------------------------------------------------ """

    def click_element(self, element: webelement) -> None:
        """
        Purpose - Clicking an web element with error handling

        Param - element: The web element to be clicked
        """
        try:
            # click element
            element.click()
            # wait
            self.driver.implicitly_wait(5)
            # return true
            return True
        except ElementNotInteractableException as e:
            print(e)
            print(
                """Could not click\n1. Element is not visible\n2. Element is present in off screen (After scroll down it will display)\n3. Element is present behind any other element\n4. Element is disabled"""
            )
            print(f"element display state is {element.is_displayed()}")
            # return false
            return False
        except AttributeError as e:
            print(e)
            # return false
            return False

    def click_elements(self, element_list: list) -> None:
        """
        Purpose - Clicking multiple web elements with error handling

        Param - element_list: The list of web elements to be clicked
        """
        try:
            for element in element_list:
                # click element
                element.click()
                # wait
                self.driver.implicitly_wait(5)
            # return true
            return True
        except ElementNotInteractableException as e:
            print(e)
            print(
                """Could not click\n1. Element is not visible\n2. Element is present in off screen (After scroll down it will display)\n3. Element is present behind any other element\n4. Element is disabled"""
            )
            print(f"element display state is {element.is_displayed()}")
            # return false
            return False
        except AttributeError as e:
            print(e)
            # return false
            return False

    """ ------------------------------------------ Window/Tab Methods ------------------------------------------------ """

    def create_new_tab(self, tab_name):
        """
        Purpose - Create new tab

        Param - tab_name: The name of the new tab to be created
        """
        self.driver.execute_script(f"window.open('', '{tab_name}');")

    def switch_tab(self, tab_name):
        """
        Purpose - Switch Tab

        Param - tab_name: A dict of web elements to parse
        """
        self.driver.switch_to.window(tab_name)

    def close_all_but_current(self):
        """
        Purpose - Close all tabs but current
        """
        # Get the current window handle (the main window)
        current_window_handle = self.driver.current_window_handle
        # Loop through the window handles and close all windows except the main window
        for window_handle in self.driver.window_handles:
            if window_handle != current_window_handle:
                self.driver.switch_to.window(
                    window_handle
                )  # Switch to the window to close
                self.driver.close()  # Close the window
        # Switch back to the main window
        self.driver.switch_to.window(current_window_handle)

    def switch_to_other_tab(self):
        """
        Purpose - Switch to other tab
        """
        # if window handles list is equal to 2
        if len(self.driver.window_handles) == 2:
            # Get the current tab handle (the main window)
            current_window_handle = self.driver.current_window_handle
            # Loop through the tab handles and switch to the one that is not current
            for window_handle in self.driver.window_handles:
                if window_handle != current_window_handle:
                    # switch to other tab
                    self.driver.switch_to.window(window_handle)
        else:
            print(
                f"Must have 2 tabs open, currently there is {len(self.driver.window_handles)}"
            )
