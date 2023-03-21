import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .api_calls import linkedin_scrapper_api_calls as link_api
from .objects import Scraper, PersonSearch, JobsSearch
import os
from linkedin_scraper import actions
from linkedin_scraper import list_classes as li_cl
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import List


class JobSearchScrap(Scraper):
    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    keywords = None
    location = None
    refresh = None
    past_date_seconds = None
    experience_level = None
    company_name = None
    job_type = None
    on_site = None
    limit = None

    def __init__(
            self,
            linkedin_url=None,
            driver=None,
            scrape=True,
            close_on_complete=True
    ):
        self.linkedin_url = linkedin_url
        self.driver = driver
        self.logged_in = False
        self.limit = None

        if self.driver is None:
            try:
                if os.getenv("CHROMEDRIVER") is None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")
                options = Options()
                # options.add_argument('--headless')
                # options.add_argument('--disable-gpu')
                options.add_argument('start-maximized')
                self.driver = webdriver.Chrome(service=Service(driver_path), chrome_options=options)
            except Exception as e:
                self.driver = webdriver.Chrome()

        if scrape:
            actions.load_cookies(driver=self.driver)
            self.scrape(close_on_complete)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.logged_in = True
        else:
            self.logged_in = False

    def search(self,
               keywords: str or None = None,
               location: str or None = None,
               refresh: bool or None = True,
               past_date_seconds: int or None = None,
               experience_level: List[int] or None = None,
               company_name: List[str] or None = None,
               job_type: List[str] or None = None,
               on_site: List[int] or None = None,
               limit: int or None = None
               ):
        self.keywords = keywords
        self.location = location
        self.refresh = refresh
        self.past_date_seconds = past_date_seconds
        self.experience_level = experience_level
        self.company_name = company_name
        self.job_type = job_type
        self.on_site = on_site
        self.limit = limit

        if self.company_name:
            companies_data = []
            for com in self.company_name:
                company_data = link_api.get_company_ids_by_name_search(name=com)
                company_ids = [comp.get("id", None) for comp in company_data if
                               comp.get("displayName", None) == com]
                companies_data.append(",".join(company_ids))
            self.company_name = ",".join(companies_data)

        if self.location:
            geo_data = link_api.get_geo_location_ids_by_name_search(name=self.location)
            if len(geo_data) > 0:
                self.location = geo_data[0].get("id", "")
            else:
                self.location = ""

        self.linkedin_url = "https://www.linkedin.com/jobs/search/?"
        if self.keywords:
            self.linkedin_url = f"{self.linkedin_url}&keywords={self.keywords}"
        if type(self.location) is str:
            self.linkedin_url = f"{self.linkedin_url}&geoId={self.location}"
        if type(self.company_name) is str:
            self.linkedin_url = f"{self.linkedin_url}&f_C={self.company_name}"
        if self.refresh:
            self.linkedin_url = f"{self.linkedin_url}&refresh={self.refresh}"
        if self.past_date_seconds:
            self.linkedin_url = f"{self.linkedin_url}&f_TPR=r{self.past_date_seconds}"
        if self.experience_level:
            data = ",".join([str(li_cl.get_experience_level(exp)) for exp in self.experience_level])
            self.linkedin_url = f"{self.linkedin_url}&f_E={data}"
        if self.job_type:
            data = ",".join([li_cl.get_job_type(job) for job in self.job_type])
            self.linkedin_url = f"{self.linkedin_url}&f_JT={data}"
        if self.on_site:
            data = ",".join([str(li_cl.get_on_site(ons)) for ons in self.on_site])
            self.linkedin_url = f"{self.linkedin_url}&f_WT={data}"

        if self.logged_in:
            return self.scrape_logged_in()
        else:
            return self.scrap_logged_out()

    def scrape_job_card(self, item):
        try:
            item = item.find_element(By.XPATH, "div").find_element(By.XPATH, "div") \
                .find_element(By.XPATH, "div").find_elements(By.XPATH, "div")[1]

            job_details = item.find_elements(By.XPATH, "div")
            job_title = ""
            job_link = ""
            company_name = ""
            company_link = ""
            job_location = ""
            try:
                job_title = job_details[0].text
            except Exception as e:
                pass
            try:
                job_link = job_details[0].find_element(By.XPATH, 'a').get_attribute("href")
            except Exception as e:
                pass
            try:
                company_name = job_details[1].text
            except Exception as e:
                pass
            try:
                company_link = job_details[1].find_element(By.XPATH, 'a').get_attribute("href")
            except Exception as e:
                pass
            try:
                job_location = job_details[2].text
            except Exception as e:
                pass
            job = JobsSearch(job_title=job_title, job_link=job_link, company_name=company_name,
                             company_link=company_link, job_location=job_location)
            return job
        except Exception as e:
            return None

    def scrape_job_card_logout(self, item):
        try:
            job_title = ""
            job_link = ""
            company_name = ""
            company_link = ""
            job_location = ""
            try:
                job_link = item.find_element(By.XPATH, '..').find_element(By.XPATH, 'a').get_attribute('href')
            except Exception as e:
                try:
                    job_link = item.find_element(By.XPATH, '..').get_attribute('href')
                except Exception as e:
                    pass
                pass
            try:
                job_title = item.find_element(By.XPATH, 'h3').text
            except Exception as e:
                pass
            try:
                company_name = item.find_element(By.XPATH, 'h4').text
            except Exception as e:
                pass
            try:
                company_link = item.find_element(By.XPATH, 'h4').find_element(By.XPATH, 'a').get_attribute('href')
            except Exception as e:
                pass
            try:
                job_location = item.find_element(By.XPATH, 'div').find_element(By.XPATH, 'span').text
            except Exception as e:
                pass
            job = JobsSearch(job_title=job_title, job_link=job_link, company_name=company_name,
                             company_link=company_link, job_location=job_location)
            return job
        except Exception as e:
            return None

    def scrape_logged_in(self):

        data_records = 1
        job_results = []
        while True:
            self.driver.get(f"{self.linkedin_url}"
                            f"&start={data_records}")
            self.wait(3)
            if "No matching jobs found." in self.driver.find_element(By.XPATH, '//body').text:
                return [j.__repr__() for j in job_results]
            self.scroll_to_half(class_name="jobs-search-results-list")
            self.scroll_to_bottom(class_name="jobs-search-results-list")
            self.wait(1)
            li = self.get_elements_by_time(by=By.XPATH,
                                           value="//li[contains(@class,'jobs-search-results__list-item')]",
                                           base=self.driver, single=False, seconds=5)
            if li is None or len(li) == 0:
                break

            for item in li:
                result_data = self.scrape_job_card(item)
                if result_data:
                    job_results.append(result_data)
                if self.limit:
                    if len(job_results) >= self.limit:
                        return [j.__repr__() for j in job_results]
            data_records = data_records + len(li)
        return [j.__repr__() for j in job_results]

    def scrap_logged_out(self):
        data_records = 1
        job_results = []
        total_list = []

        self.driver.get(f"{self.linkedin_url}")
        self.wait(3)
        if "We couldn’t find \"" in self.driver.find_element(By.XPATH, "//body").text:
            return [j.__repr__() for j in job_results]
        temp = self.driver.find_elements(By.XPATH, "//div[contains(@class,'base-search-card__info')]")
        update_time = datetime.datetime.now()
        while True:
            if len(total_list) == len(temp):
                pass
            else:
                update_time = datetime.datetime.now()
            total_list = temp
            self.scroll_to_bottom()
            self.wait(1)
            temp = self.driver.find_elements(By.XPATH, "//div[contains(@class,'base-search-card__info')]")
            if (datetime.datetime.now() - update_time).seconds > 5:
                break

        for item in total_list:
            result_data = self.scrape_job_card_logout(item)
            if result_data:
                job_results.append(result_data)
            if self.limit:
                if len(job_results) >= self.limit:
                    return [j.__repr__() for j in job_results]
        return [j.__repr__() for j in job_results]
