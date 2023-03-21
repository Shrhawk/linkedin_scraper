from dataclasses import dataclass
from time import sleep

from selenium.webdriver import Chrome

from . import constants as c

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class Contact:
    name: str = None
    occupation: str = None
    url: str = None

    def __repr__(self) -> dict:
        return {
            "name": self.name,
            "occupation": self.occupation,
            "url": self.url
        }


@dataclass
class PersonSearch:
    link: str = None
    name: str = None
    description: str = None
    location: str = None

    def __repr__(self) -> dict:
        return {
            "link": self.link,
            "name": self.name,
            "description": self.description,
            "location": self.location
        }


@dataclass
class JobsSearch:
    job_title: str = None
    job_link: str = None
    company_name: str = None
    company_link: str = None
    job_location: str = None

    def __repr__(self) -> dict:
        return {
            "job_title": self.job_title,
            "job_link": self.job_link,
            "company_name": self.company_name,
            "company_link": self.company_link,
            "job_location": self.job_location
        }


@dataclass
class Institution:
    institution_name: str = None
    linkedin_url: str = None
    website: str = None
    industry: str = None
    type: str = None
    headquarters: str = None
    company_size: int = None
    founded: int = None

    def __repr__(self) -> dict:
        return {
            "institution_name": self.institution_name,
            "linkedin_url": self.linkedin_url,
            "website": self.website,
            "industry": self.industry,
            "type": self.type,
            "headquarters": self.headquarters,
            "company_size": self.company_size,
            "founded": self.founded
        }


@dataclass
class Experience(Institution):
    from_date: str = None
    to_date: str = None
    description: str = None
    position_title: str = None
    duration: str = None
    location: str = None

    def __repr__(self) -> dict:
        result = super().__repr__()
        result.update(
            {
                "from_date": self.from_date,
                "to_date": self.to_date,
                "description": self.description,
                "position_title": self.position_title,
                "duration": self.duration,
                "location": self.location
            }
        )
        return result


@dataclass
class Education(Institution):
    from_date: str = None
    to_date: str = None
    description: str = None
    degree: str = None

    def __repr__(self) -> dict:
        result = super().__repr__()
        result.update({
            "from_date": self.from_date,
            "to_date": self.to_date,
            "description": self.description,
            "degree": self.degree
        })
        return result


@dataclass
class InterestTemplate:
    name: str = None
    url: str = None
    followers: str = None
    description: str = None

    def __repr__(self) -> dict:
        data = {
            "name": self.name,
            "url": self.url
        }
        if self.followers:
            data.update({
                "followers": self.followers
            })
        if self.description:
            data.update({
                "description": self.description
            })
        return data


@dataclass
class Interest:
    companies: list
    schools: list
    top_voices: list
    groups: list
    news_letters: list

    def __init__(self):
        self.companies = []
        self.schools = []
        self.news_letters = []
        self.top_voices = []
        self.groups = []

    def __repr__(self) -> dict:
        return {
            "companies": [com.__repr__() for com in self.companies],
            "schools": [sch.__repr__() for sch in self.schools],
            "top_voices": [top.__repr__() for top in self.top_voices],
            "groups": [grp.__repr__() for grp in self.groups],
            "news_letters": [let.__repr__() for let in self.news_letters]
        }


@dataclass
class Accomplishment(Institution):
    category = None
    title = None

    def __repr__(self) -> dict:
        result = super().__repr__()
        result.update(
            {
                "category": self.category,
                "title": self.title
            }
        )
        return result


@dataclass
class Scraper:
    driver: Chrome = None
    WAIT_FOR_ELEMENT_TIMEOUT = 5
    TOP_CARD = "pv-top-card"

    @staticmethod
    def wait(duration):
        sleep(int(duration))

    def focus(self):
        self.driver.execute_script('alert("Focus window")')
        self.driver.switch_to.alert.accept()

    def get_elements_by_time(self, by=By.CLASS_NAME, value='', seconds=5, base=None, single=True, element_count=None):
        counter = 0
        if base is None:
            base = self.driver
        while counter < seconds:
            elements = base.find_elements(by=by, value=value)
            if len(elements) == 0:
                pass
            else:
                if single:
                    return elements[0]
                elif element_count is None:
                    return elements
                else:
                    if len(elements) > element_count + 1:
                        return elements
            counter = counter + 1
            self.wait(1)
        return None

    def get_element_text(self, by=By.CLASS_NAME, value='', seconds=3, base=None):
        element = self.get_elements_by_time(by=by, value=value, seconds=seconds, base=base)
        if element:
            return element.text.strip()
        else:
            return ""

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    by,
                    name
                )
            )
        )

    def wait_for_all_elements_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_all_elements_located(
                (
                    by,
                    name
                )
            )
        )

    def is_signed_in(self):
        try:
            WebDriverWait(self.driver, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.CLASS_NAME,
                        c.VERIFY_LOGIN_ID,
                    )
                )
            )

            self.driver.find_element(By.CLASS_NAME, c.VERIFY_LOGIN_ID)
            return True
        except Exception as e:
            pass
        return False

    def scroll_to_half(self, class_name: str or None = None):
        try:
            if class_name:
                self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f"my_div.scrollTo(0,my_div.scrollHeight);"
                )
            else:
                self.driver.execute_script(
                    "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
                )
        except Exception as e:
            pass

    def scroll_to_top(self, class_name: str or None = None):
        try:
            if class_name:
                self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f"my_div.scrollTo(0,0);"
                )
            else:
                self.driver.execute_script(
                    "window.scrollTo(0, 0);"
                )
        except Exception as e:
            pass

    def get_document_height(self, class_name: str or None = None):
        try:
            if class_name:
                return self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f"return my_div.scrollHeight;"
                )
            else:
                return self.driver.execute_script(
                    "return document.body.scrollHeight;"
                )
        except Exception as e:
            pass

    def scroll_to_bottom(self, class_name: str or None = None):
        try:
            if class_name:
                self.driver.execute_script(
                    f"my_div = document.getElementsByClassName('{class_name}')[0];"
                    f"my_div.scrollTo(0,my_div.scrollHeight);"
                )
            else:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
        except Exception as e:
            pass

    def scroll_class_name_element_to_page_percent(self, class_name: str, page_percent: float):
        self.driver.execute_script(
            f'elem = document.getElementsByClassName("{class_name}")[0]; elem.scrollTo(0, elem.scrollHeight*{str(page_percent)});'
        )

    def __find_element_by_class_name__(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
            return True
        except Exception as e:
            pass
        return False

    def __find_element_by_xpath__(self, tag_name):
        try:
            self.driver.find_element(By.XPATH, tag_name)
            return True
        except Exception as e:
            pass
        return False

    def __find_enabled_element_by_xpath__(self, tag_name):
        try:
            elem = self.driver.find_element(By.XPATH, tag_name)
            return elem.is_enabled()
        except Exception as e:
            pass
        return False

    @classmethod
    def __find_first_available_element__(cls, *args):
        for elem in args:
            if elem:
                return elem[0]
