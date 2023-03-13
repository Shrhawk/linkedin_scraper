import os
from typing import List
from time import sleep
import urllib.parse
from .objects import Scraper
from .jobs import Job
from selenium.webdriver.common.by import By


class JobSearch(Scraper):
    AREAS = ["recommended_jobs", None, "still_hiring", "more_jobs"]

    def __init__(self, driver, base_url="https://www.linkedin.com/jobs/", close_on_complete=False,
                 scrape=True, scrape_recommended_jobs=True):
        super().__init__()
        self.driver = driver
        self.base_url = base_url

        if scrape:
            self.scrape(close_on_complete, scrape_recommended_jobs)

    def __repr__(self) -> dict:
        results = {
            "AREAS": self.AREAS
        }
        for area in self.AREAS:
            if area is None:
                continue
            jobs = getattr(self, area)
            results.update({
                area: [job.__repr__() for job in jobs]
            })
        results.update({
            "base_url": self.base_url
        })
        return results

    def scrape(self, close_on_complete=True, scrape_recommended_jobs=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete, scrape_recommended_jobs=scrape_recommended_jobs)
        else:
            raise NotImplemented("This part is not implemented yet")

    def scrape_job_card(self, base_element) -> Job:
        job_div = self.wait_for_element_to_load(name="job-card-list__title", base=base_element)
        job_title = job_div.text.strip()
        linkedin_url = job_div.get_attribute("href")
        company = base_element.find_element(By.CLASS_NAME, "job-card-container__primary-description")
        location = base_element.find_element(By.CLASS_NAME, "job-card-container__metadata-item")
        job = Job(linkedin_url=linkedin_url, job_title=job_title,
                  company=company, location=location, scrape=False, driver=self.driver)
        return job

    def scrape_logged_in(self, close_on_complete=True, scrape_recommended_jobs=True):
        driver = self.driver
        driver.get(self.base_url)
        if scrape_recommended_jobs:
            self.focus()
            sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)
            job_area = self.wait_for_element_to_load(name="scaffold-finite-scroll__content")
            areas = self.wait_for_all_elements_to_load(name="artdeco-card", base=job_area)
            for i, area in enumerate(areas):
                area_name = self.AREAS[i]
                if not area_name:
                    continue
                area_results = []
                for job_posting in area.find_elements(By.CLASS_NAME, "jobs-job-board-list__item"):
                    job = self.scrape_job_card(job_posting)
                    area_results.append(job)
                setattr(self, area_name, area_results)
        if close_on_complete:
            driver.quit()
        return

    def scrape_job_card_search(self, base_element) -> Job:
        job_div = base_element.find_element(By.XPATH, 'div')\
            .find_element(By.XPATH, 'div')\
            .find_element(By.XPATH, 'div')\
            .find_elements(By.XPATH, 'div')[1]
        job_data = job_div.find_elements(By.XPATH, 'div')
        job_title = job_data[0].text
        linkedin_url = job_data[0].find_element(By.XPATH, 'a').get_attribute("href")
        company = job_data[1].text
        company_linkedin_url = job_data[1].find_element(By.XPATH, 'a').get_attribute("href")
        location = job_data[2].text

        job = Job(linkedin_url=linkedin_url,
                  job_title=job_title, company=company, location=location,
                  company_linkedin_url=company_linkedin_url,
                  scrape=False, driver=self.driver)
        return job

    def search(self, search_term: str) -> List[dict]:
        url = os.path.join(self.base_url, "search") + f"?keywords={urllib.parse.quote(search_term)}&refresh=true"
        self.driver.get(url)
        self.scroll_to_bottom()
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)
        job_listing_class_name = "jobs-search-results-list"
        job_listing = self.wait_for_element_to_load(name=job_listing_class_name)
        self.scroll_class_name_element_to_page_percent(job_listing_class_name, 0.3)
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)
        self.scroll_class_name_element_to_page_percent(job_listing_class_name, 0.6)
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)
        self.scroll_class_name_element_to_page_percent(job_listing_class_name, 1)
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)
        job_results = []
        job_cards = self.driver.find_elements(By.XPATH, "//li[contains(@class,'jobs-search-results__list-item')]")
        for job_card in job_cards:
            try:
                job = self.scrape_job_card_search(job_card)
                job_results.append(job)
            except Exception as e1:
                print(f"Exception -> "+str(e1))
        return [job.__repr__() for job in job_results]
