from .objects import Scraper
from selenium.webdriver.common.by import By


class Job(Scraper):

    def __init__(
        self,
        linkedin_url=None,
        job_title=None,
        company=None,
        company_linkedin_url=None,
        location=None,
        posted_date=None,
        applicant_count=None,
        job_description=None,
        benefits=None,
        driver=None,
        close_on_complete=True,
        scrape=True,
    ):
        super().__init__()
        self.linkedin_url = linkedin_url
        self.job_title = job_title
        self.driver = driver
        self.company = company
        self.company_linkedin_url = company_linkedin_url
        self.location = location
        self.posted_date = posted_date
        self.applicant_count = applicant_count
        self.job_description = job_description
        self.benefits = benefits

        if scrape:
            self.scrape(close_on_complete)

    def __repr__(self) -> dict:
        return {
            "linkedin_url": self.linkedin_url,
            "job_title": self.job_title,
            "company": self.company,
            "company_linkedin_url": self.company_linkedin_url,
            "location": self.location,
            "posted_date": self.posted_date,
            "applicant_count": self.applicant_count,
            "job_description": self.job_description,
            "benefits": self.benefits
        }

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            return

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        driver.get(self.linkedin_url)
        self.focus()
        element = self.get_elements_by_time(single=True, value="jobs-unified-top-card__job-title")
        if element is None:
            return
        self.job_title = self.get_element_text(value='jobs-unified-top-card__job-title')
        self.company = self.get_element_text(value="jobs-unified-top-card__company-name")
        self.company_linkedin_url = self.wait_for_element_to_load(name="jobs-unified-top-card__company-name")\
            .find_element(By.TAG_NAME, "a").get_attribute("href")
        self.location = self.get_element_text(value="jobs-unified-top-card__bullet")
        self.posted_date = self.get_element_text(value="jobs-unified-top-card__posted-date")
        self.applicant_count = self.get_element_text(value="jobs-unified-top-card__applicant-count")
        self.job_description = self.get_element_text(value="jobs-description")
        self.benefits = self.get_element_text(value="jobs-unified-description__salary-main-rail-card")
        if close_on_complete:
            driver.close()
