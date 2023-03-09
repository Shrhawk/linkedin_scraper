import os

from linkedin_scraper import actions
from linkedin_scraper.person import Person
from linkedin_scraper.company import Company
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
#options.add_argument('--headless')
#options.add_argument('--disable-gpu')
#options.add_argument('start-maximized')

driver = webdriver.Chrome(service=Service("drivers/chromedriver"), chrome_options=options)

email = os.getenv("LINKEDIN_USER")
password = os.getenv("LINKEDIN_PASSWORD")
actions.login(driver, email, password) # if email and password isnt given, it'll prompt in terminal


#rick_fox = Person("https://www.linkedin.com/in/rifox", driver=driver, close_on_complete=False)
#iggy = Person("https://www.linkedin.com/in/andre-iguodala-65b48ab5", driver=driver, close_on_complete=False)
#anirudra = Person("https://in.linkedin.com/in/anirudra-choudhury-109635b1", driver=driver, close_on_complete=False)

print("OK")
