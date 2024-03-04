#!/usr/local/DCOM/python/nagPy3/bin/python

import argparse
import sys
import time
import re
from os import environ
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

parser = argparse.ArgumentParser(description="Check OpenGear Console Server")
parser.add_argument(
    "--url", type=str, help="url of the OpenGear Console Server", required=True
)
parser.add_argument("--username", type=str, help="username to login", required=True)
parser.add_argument("--password", type=str, help="password to login", required=True)
args = parser.parse_args()

backendPerformance = ""
frontendPerformance = ""
msg = ""
binary = FirefoxBinary("/usr/bin/firefox")


def main(url):
    global frontendPerformance
    global backendPerformance
    global msg
    environ["MOZ_HEADLESS"] = "1"
    try:
        browser = webdriver.Firefox(
            firefox_binary=binary,
            executable_path="/usr/local/DCOM/webdriver/firefox/bin/geckodriver",
        )
        browser.set_page_load_timeout(10)
        browser.get(url)
        # print('Title: %s' % browser.title)
        navigationStart = browser.execute_script(
            "return window.performance.timing.navigationStart"
        )
        responseStart = browser.execute_script(
            "return window.performance.timing.responseStart"
        )
        domComplete = browser.execute_script(
            "return window.performance.timing.domComplete"
        )
        backendPerformance = (responseStart - navigationStart) / 100.00
        frontendPerformance = (domComplete - responseStart) / 100.00
        element_driver = browser.find_element_by_name("username")
        element_driver.send_keys(args.username)
        status = element_driver.get_attribute("value")
        # print('Value entered: ' + status)
        time.sleep(1)
        element_driver = browser.find_element_by_name("password")
        element_driver.send_keys(args.password)
        status = element_driver.get_attribute("value")
        # print('Value entered: ' + status)
        time.sleep(1)
        element_driver = browser.find_element(By.XPATH, "//input[@name='apply']")
        element_driver.click()
        time.sleep(3)
        try:
            status = browser.find_element(By.CLASS_NAME, "status")
            modelRegex = re.compile(r"<b>Model</b>: CM7148-2-DAC")
            model = modelRegex.search(status.get_attribute("innerHTML"))
            # print(model.group())
            if model.group() == "<b>Model</b>: CM7148-2-DAC":
                print("Login Successful")
                msg = f"Login to {browser.title} Successful"
                browser.close()
                browser.quit()
                return 0
            else:
                print("Login Failed")
                msg = "Login to {browser.title} Failed"
                browser.close()
                browser.quit()
                return 1
        except Exception as e:
            msg = "Exception, username or password issue."
            # print(msg)
            # print(e)
            browser.close()
            browser.quit()
            return 1

        time.sleep(1)
        element_driver = browser.find_element(
            By.CSS_SELECTOR, "td.top-button:nth-child(4) > a:nth-child(3)"
        )
        element_driver.click()
        browser.close()
        browser.quit()
    except Exception as e:
        # print (f"No Response from {args.url}\n"+"Exception Error: {0}".format(e))
        msg = f"No Response from {args.url}\n" + "Exception Error: {0}".format(e)
        browser.close()
        browser.quit()
        return 3
    return 0


if __name__ == "__main__":
    status = main(url=args.url)
    if status == 0:
        print(
            "OK: {0}".format(msg)
            + "|"
            + "backendPerformance={0}s".format(backendPerformance)
            + ";;;,"
            + "frontendPerformance={0}s".format(frontendPerformance)
            + ";;;"
        )
    elif status == 1:
        print(
            "WARNING: {0}".format(msg)
            + "|backendPerformance=0s;;;,"
            + "frontendPerformance=0;;;"
        )
    elif status == 2:
        print(
            "CRITICAL: {0}".format(msg)
            + "|backendPerformance=0s;;;,"
            + "frontendPerformance=0;;;"
        )
    elif status == 3:
        print(
            "UNKNOWN: {0}".format(msg)
            + "|backendPerformance=0s;;;,"
            + "frontendPerformance=0;;;"
        )
    sys.exit(status)
