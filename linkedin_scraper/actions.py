import getpass
import pickle

from . import constants as c
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os

def __prompt_email_password():
    u = input("Email: ")
    p = getpass.getpass(prompt="Password: ")
    return u, p


def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'


def load_cookies(driver):
    driver.get('https://www.linkedin.com/')
    if os.path.isfile(c.COOKIE_FILE_NAME):
        with open(c.COOKIE_FILE_NAME, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.get('https://www.linkedin.com/feed/')
            sleep(2)


def save_cookies(driver):
    pickle.dump(driver.get_cookies(), open(c.COOKIE_FILE_NAME, 'wb'))


def login(driver, email=None, password=None, cookie=None, timeout=10):

    load_cookies(driver=driver)
    counter = 0
    while driver.current_url == 'https://www.linkedin.com/feed/' and counter < 5:
        element = driver.find_elements(By.CLASS_NAME, c.VERIFY_LOGIN_ID)
        if len(element) > 0:
            return
        counter = counter + 1
        sleep(3)

    if not email or not password:
        email, password = __prompt_email_password()

    driver.get("https://www.linkedin.com/login")

    try:
        email_elem = driver.find_element(By.ID, "username")
        email_elem.send_keys(email)
    except:
        pass
    password_elem = driver.find_element(By.ID, "password")
    password_elem.send_keys(password)
    password_elem.submit()

    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        remember = driver.find_element(By.ID, c.REMEMBER_PROMPT)
        if remember:
            remember.submit()

    counters = 0
    while counters < timeout:
        sleep(1)
        element = driver.find_elements(By.CLASS_NAME, c.VERIFY_LOGIN_ID)
        if len(element) == 0:
            pass
        else:
            break
    save_cookies(driver)

def _login_with_cookie(driver, cookie):
    driver.get("https://www.linkedin.com/login")
    driver.add_cookie({
        "name": "li_at",
        "value": cookie
    })
