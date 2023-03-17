import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .objects import Scraper
import time
import os
import json
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from linkedin_scraper import actions
from selenium.webdriver import ActionChains

AD_BANNER_CLASSNAME = ('ad-banner-container', '__ad')


def getchildren(elem):
    return elem.find_elements(By.XPATH, ".//*")


class CompanySummary(object):
    linkedin_url = None
    name = None
    followers = None

    def __init__(self, linkedin_url: str or None = None, name=None, followers=None):
        self.linkedin_url = linkedin_url.split("?")[0] if linkedin_url else linkedin_url
        self.name = name
        self.followers = followers

    def __repr__(self):
        if self.followers is None:
            return """ {name} """.format(name=self.name)
        else:
            return """ {name} {followers} """.format(name=self.name, followers=self.followers)


class Company(Scraper):
    linkedin_url = None
    name = None
    about_us = None
    website = None
    headquarters = None
    founded = None
    industry = None
    company_type = None
    company_size = None
    specialties = None
    showcase_pages = []
    affiliated_companies = []
    employees = []
    headcount = None

    def __init__(self,
                 linkedin_url=None,
                 name=None,
                 about_us=None,
                 website=None,
                 headquarters=None,
                 founded=None,
                 industry=None,
                 company_type=None,
                 company_size=None,
                 specialties=None,
                 showcase_pages=[],
                 affiliated_companies=[],
                 driver=None,
                 scrape=True,
                 get_employees=True,
                 close_on_complete=True):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about_us = about_us
        self.website = website
        self.headquarters = headquarters
        self.founded = founded
        self.industry = industry
        self.company_type = company_type
        self.company_size = company_size
        self.specialties = specialties
        self.showcase_pages = showcase_pages
        self.affiliated_companies = affiliated_companies
        self.driver = driver

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") is None:
                    driver_path = os.path.join(os.path.dirname(__file__), 'drivers/chromedriver')
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                options = Options()
                # options.add_argument('--headless')
                # options.add_argument('--disable-gpu')
                options.add_argument('start-maximized')
                self.driver = webdriver.Chrome(service=Service(driver_path), chrome_options=options)
            except:
                self.driver = webdriver.Chrome()
        if scrape:
            actions.load_cookies(driver=self.driver)
            self.driver.get(linkedin_url)
            self.scrape(get_employees=get_employees, close_on_complete=close_on_complete)

    def __get_text_under_subtitle(self, elem):
        return "\n".join(elem.text.split("\n")[1:])

    def __get_text_under_subtitle_by_class(self, driver, class_name):
        return self.__get_text_under_subtitle(driver.find_element(By.CLASS_NAME, class_name))

    def scrape(self, get_employees=True, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(get_employees=get_employees, close_on_complete=close_on_complete)
        else:
            self.scrape_not_logged_in(get_employees=get_employees, close_on_complete=close_on_complete)

    def __parse_employee__(self, employee_raw):
        employee_object = {
            "name": "",
            "designation": "",
            "linkedin_url": ""
        }
        try:
            employee_object['name'] = (employee_raw.text.split("\n") or [""])[0].strip()
            employee_object['designation'] = (employee_raw.text.split("\n") or [""])[1].strip()
        except:
            pass
        try:
            employee_object['designation'] = (employee_raw.text.split("\n") or [""])[3].strip()
        except:
            pass
        try:
            employee_object['linkedin_url'] = employee_raw.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            pass
        return employee_object

    def get_elements_by_count(self, by=By.XPATH, path="", count=5, retries=5):
        again = 0
        while again < retries + 1:
            click_buttons = self.driver.find_elements(by, path)
            if len(click_buttons) > count - 1:
                return click_buttons
            else:
                self.wait(1)
                again = again + 1
        return None

    def get_employees(self, wait_time=10):
        """artdeco-button--1"""
        self.driver.get(os.path.join(self.linkedin_url, 'people'))
        _ = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((
            By.XPATH, "//div[contains(@class,'org-grid__content-height-enforcer')]")))
        click_buttons = self.get_elements_by_count(
            by=By.XPATH,
            path="//button[contains(@class,'artdeco-button--1')]",
            count=5,
            retries=5
        )

        total_list = []
        temp = self.driver.find_elements(By.XPATH, "//li[contains(@class,'grid__col--lg-8')]")
        if len(click_buttons) > 0:
            update_time = datetime.datetime.now()
            while True:
                if len(total_list) == len(temp):
                    pass
                else:
                    update_time = datetime.datetime.now()
                total_list = temp
                click_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class,'artdeco-button--1')]")
                action = ActionChains(self.driver)
                action.click(on_element=click_buttons[4])
                action.perform()
                self.scroll_to_bottom()
                self.wait(1)
                temp = self.driver.find_elements(By.XPATH, "//li[contains(@class,'grid__col--lg-8')]")
                if (datetime.datetime.now() - update_time).seconds > 10:
                    break
        total = []
        list_css = "list-style-none"
        next_xpath = '//button[@aria-label="Next"]'
        driver = self.driver
        results_list = driver.find_element(By.CLASS_NAME, list_css)
        results_li = results_list.find_elements(By.TAG_NAME, "li")
        for res in results_li:
            total.append(self.__parse_employee__(res))
        return total

    def scrape_logged_in(self, get_employees=True, close_on_complete=True):
        driver = self.driver

        driver.get(self.linkedin_url)

        _ = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@dir="ltr"]')))

        navigation = driver.find_element(By.CLASS_NAME, "org-page-navigation__items ")

        self.name = driver.find_element(By.XPATH, '//span[@dir="ltr"]').text.strip()

        # Click About Tab or View All Link
        try:
            self.__find_first_available_element__(
                navigation.find_elements(By.XPATH, "//a[@data-control-name='page_member_main_nav_about_tab']"),
                navigation.find_elements(By.XPATH, "//a[@data-control-name='org_about_module_see_all_view_link']"),
            ).click()
        except:
            driver.get(os.path.join(self.linkedin_url, "about"))
        _ = WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'section')))
        time.sleep(3)
        grid = driver.find_element(By.CLASS_NAME, "artdeco-card.p5.mb4")
        descWrapper = grid.find_elements(By.TAG_NAME, "p")
        if len(descWrapper) > 0:
            self.about_us = descWrapper[0].text.strip()
        labels = grid.find_elements(By.TAG_NAME, "dt")
        values = grid.find_elements(By.TAG_NAME, "dd")
        num_attributes = min(len(labels), len(values))
        x_off = 0
        for i in range(num_attributes):
            txt = labels[i].text.strip()
            if txt == 'Website':
                self.website = values[i + x_off].text.strip()
            elif txt == 'Industry':
                self.industry = values[i + x_off].text.strip()
            elif txt == 'Company size':
                self.company_size = values[i + x_off].text.strip()
                if len(values) > len(labels):
                    x_off = 1
            elif txt == 'Headquarters':
                self.headquarters = values[i + x_off].text.strip()
            elif txt == 'Type':
                self.company_type = values[i + x_off].text.strip()
            elif txt == 'Founded':
                self.founded = values[i + x_off].text.strip()
            elif txt == 'Specialties':
                self.specialties = "\n".join(values[i + x_off].text.strip().split(", "))
        grid = driver.find_element(By.CLASS_NAME, "mt1")
        spans = grid.find_elements(By.TAG_NAME, "span")
        for span in spans:
            txt = span.text.strip()
            if "See all" in txt and "employees on LinkedIn" in txt:
                self.headcount = int(txt.replace("See all", "").replace("employees on LinkedIn", "").strip())
        driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")
        try:
            _ = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'company-list')))
            showcase, affiliated = driver.find_elements(By.CLASS_NAME, "company-list")
            driver.find_element(By.ID, "org-related-companies-module__show-more-btn").click()
            # get showcase
            for showcase_company in showcase.find_elements(By.CLASS_NAME, "org-company-card"):
                company_summary = CompanySummary(
                    linkedin_url=showcase_company.find_element(By.CLASS_NAME, "company-name-link").get_attribute(
                        "href"),
                    name=showcase_company.find_element(By.CLASS_NAME, "company-name-link").text.strip(),
                    followers=showcase_company.find_element(By.CLASS_NAME, "company-followers-count").text.strip()
                )
                self.showcase_pages.append(company_summary)
            # affiliated company
            for affiliated_company in showcase.find_elements(By.CLASS_NAME, "org-company-card"):
                company_summary = CompanySummary(
                    linkedin_url=affiliated_company.find_element(By.CLASS_NAME, "company-name-link").get_attribute(
                        "href"),
                    name=affiliated_company.find_element(By.CLASS_NAME, "company-name-link").text.strip(),
                    followers=affiliated_company.find_element(By.CLASS_NAME, "company-followers-count").text.strip()
                )
                self.affiliated_companies.append(company_summary)
        except:
            pass
        if get_employees:
            self.employees = self.get_employees()
        driver.get(self.linkedin_url)
        if close_on_complete:
            self.driver.close()

    def scrape_not_logged_in(self, close_on_complete=True, retry_limit=10, get_employees=True):
        driver = self.driver
        retry_times = 0
        while self.is_signed_in() and retry_times <= retry_limit:
            page = driver.get(self.linkedin_url)
            retry_times = retry_times + 1
        try:
            but = self.get_elements_by_time(by=By.XPATH,
                                            value="//button[contains(@class,'contextual-sign-in-modal__modal-dismiss')]",
                                            single=True)
            action = ActionChains(self.driver)
            action.click(but)
            action.perform()

        except:
            pass
        self.name = self.get_element_text(by=By.XPATH, value="//h1[contains(@class,'top-card-layout__title')]")
        container = self.get_elements_by_time(by=By.XPATH,
                                              value="//div[contains(@class,'core-section-container__content')]")
        self.about_us = container.find_element(By.XPATH, 'p').text

        container = container.find_element(By.XPATH, 'dl')
        containers = container.find_elements(By.XPATH, 'div')
        for item in containers:
            data = item.text.replace("\n", " ")
            if "Website" in data:
                self.website = data.replace("Website", "").strip()
            elif "Company size" in data:
                self.company_size = data.replace("Company size", "").strip()
            elif "Headquarters" in data:
                self.headquarters = data.replace("Headquarters", "").strip()
            elif "Type" in data:
                self.company_type = data.replace("Type", "").strip()
            elif "Founded" in data:
                self.founded = data.replace("Founded", "").strip()
            elif "Specialties" in data:
                self.specialties = data.replace("Specialties", "").strip()

        # get showcase
        try:
            driver.find_element(By.ID, "view-other-showcase-pages-dialog").click()
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'dialog')))
            showcase_pages = driver.find_elements(By.CLASS_NAME, "company-showcase-pages")[1]
            for showcase_company in showcase_pages.find_elements(By.TAG_NAME, "li"):
                name_elem = showcase_company.find_element(By.CLASS_NAME, "name")
                company_summary = CompanySummary(
                    linkedin_url=name_elem.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    name=name_elem.text.strip(),
                    followers=showcase_company.text.strip().split("\n")[1]
                )
                self.showcase_pages.append(company_summary)
            driver.find_element(By.CLASS_NAME, "dialog-close").click()
        except:
            pass
        # affiliated company
        try:
            affiliated_pages = driver.find_element(By.CLASS_NAME, "affiliated-companies")
            for i, affiliated_page in enumerate(
                    affiliated_pages.find_elements(By.CLASS_NAME, "affiliated-company-name")):
                if i % 3 == 0:
                    affiliated_pages.find_element(By.CLASS_NAME, "carousel-control-next").click()
                company_summary = CompanySummary(
                    linkedin_url=affiliated_page.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    name=affiliated_page.text.strip()
                )
                self.affiliated_companies.append(company_summary)
        except:
            pass
        if get_employees:
            self.employees = self.get_employees()
        driver.get(self.linkedin_url)
        if close_on_complete:
            driver.close()

    def __repr__(self):
        _output = {
            'name': self.name,
            'about_us': self.about_us,
            'specialties': self.specialties,
            'website': self.website,
            'industry': self.industry,
            'company_type': self.name,
            'headquarters': self.headquarters,
            'company_size': self.company_size,
            'founded': self.founded,
            'affiliated_companies': self.affiliated_companies,
            'employees': self.employees,
            'headcount': self.headcount
        }
        return json.dumps(_output).replace('\n', '')
