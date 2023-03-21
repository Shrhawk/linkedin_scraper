from selenium import webdriver
from selenium.webdriver.common.by import By
from .objects import Scraper, PersonSearch
import os
from linkedin_scraper import actions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .api_calls import linkedin_scrapper_api_calls as link_api


class PersonSearchScrap(Scraper):
    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5
    first_name = ""
    last_name = ""
    location = ""
    keywords = ""

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

    def search(self, first_name: str = "", last_name: str = "", location: str = "", keywords: str = "",
               limit: int or None = None):
        self.first_name = first_name
        self.last_name = last_name
        self.location = location
        self.keywords = keywords
        self.limit = limit

        if self.logged_in:
            return self.scrape_logged_in()
        else:
            return self.scrap_logged_out()

    def scrape_logged_in(self):
        page = 0
        persons = []

        if self.location:
            geo_data = link_api.get_geo_location_ids_by_name_search(name=self.location)
            if len(geo_data) > 0:
                self.location = geo_data[0].get("id", "")
            else:
                self.location = ""
        while True:
            page = page + 1
            self.linkedin_url = "https://www.linkedin.com/search/results/people/?firstName=" \
                                f"{self.first_name.strip()}&lastName={self.last_name.strip()}" \
                                f"&page={page}" \
                                f"&keywords={self.keywords.strip()}&geoUrn={self.location}"
            self.driver.get(self.linkedin_url)
            self.wait(5)
            self.scroll_to_half()
            self.scroll_to_bottom()
            self.wait(2)
            li = self.get_elements_by_time(by=By.CLASS_NAME, value="reusable-search__result-container",
                                           seconds=5, single=False)
            if li is None or len(li) == 0:
                break
            for item in li:
                item = item.find_element(By.XPATH, 'div').find_element(By.XPATH, 'div')
                link = item.find_element(By.XPATH, 'div').find_element(By.XPATH, 'div') \
                    .find_element(By.XPATH, 'a').get_attribute('href')
                item = item.find_elements(By.XPATH, 'div')[1]
                item = item.find_element(By.XPATH, 'div')
                name = item.find_element(By.XPATH, 'div').text.strip().split("\n")[0]
                item = item.find_elements(By.XPATH, 'div')[1]
                description = item.find_element(By.XPATH, 'div').text
                location = ""
                try:
                    location = item.find_elements(By.XPATH, 'div')[1].text
                except Exception as e:
                    pass
                p = PersonSearch(link=link, name=name, description=description, location=location)
                persons.append(p)
                if self.limit is None:
                    pass
                else:
                    if len(persons) >= self.limit:
                        return [p.__repr__() for p in persons]

        return [p.__repr__() for p in persons]

    def scrap_logged_out(self):
        persons = []
        self.linkedin_url = "https://www.linkedin.com/pub/dir?firstName=" \
                            f"{self.first_name.strip()}&lastName={self.last_name.strip()}" \
                            f"&keywords={self.keywords.strip()}" \
                            "&trk=people-guest_people-search-bar_search-submit".replace(" ", "+")
        self.driver.get(self.linkedin_url)
        li = self.get_elements_by_time(by=By.CLASS_NAME, value="pserp-layout__profile-result-list-item",
                                       seconds=5, single=False)
        if li is None or len(li) == 0:
            return None
        for item in li:
            item = item.find_element(By.XPATH, 'a')
            link = item.get_attribute('href')
            item = item.find_elements(By.XPATH, 'a')[1]
            name = item.find_element(By.XPATH, 'h3').text
            description = item.find_element(By.XPATH, 'h4').text
            item = item.find_element(By.XPATH, 'div')
            location = item.find_element(By.XPATH, 'p').text
            p = PersonSearch(link=link, name=name, description=description, location=location)
            persons.append(p)
            if self.limit:
                if len(persons) >= self.limit:
                    return [p.__repr__() for p in persons]
        return [p.__repr__() for p in persons]
