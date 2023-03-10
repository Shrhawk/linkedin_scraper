from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact, InterestTemplate
import os
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
import json

ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)


class Person(Scraper):
    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(
            self,
            linkedin_url=None,
            name=None,
            about=None,
            experiences=None,
            educations=None,
            interests=None,
            accomplishments=None,
            company=None,
            job_title=None,
            contacts=None,
            driver=None,
            get=True,
            scrape=True,
            close_on_complete=True,
            time_to_wait_after_login=0,
    ):
        self.location = None
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interest = Interest or None
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []
        self.driver = driver
        if self.driver is None:
            try:
                if os.getenv("CHROMEDRIVER") is None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                self.driver = webdriver.Chrome(driver_path)
            except:
                self.driver = webdriver.Chrome()

        if get:
            self.driver.get(linkedin_url)

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interest = interest

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            div.find_element(By.TAG_NAME, "button").click()
        except Exception as e:
            pass

    def is_open_to_work(self):
        try:
            return "#OPEN_TO_WORK" in self.driver.find_element(
                By.CLASS_NAME, "pv-top-card-profile-picture").find_element(
                By.TAG_NAME, "img").get_attribute("title")
        except:
            return False

    def get_experiences(self):
        url = os.path.join(self.linkedin_url, "details/experience")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.ID, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH,
                                                                                  "//section[contains(@id,'ember')]")))
        self.wait(3)
        main_list = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions) \
            .until(expected_conditions.presence_of_all_elements_located((By.XPATH, "//section[contains(@id,'ember')]")))
        for item_ in main_list:
            """
            items = item.find_elements(By.XPATH, "div[contains(@class,'pvs-header__container')]")
            if len(items) is 0:
                continue
            elif "Experience" not in items[0].text:
                continue
            """
            if item_.text.startswith("Experience"):
                temp_list = item_.find_elements(By.XPATH, 'div')
                for item in temp_list:
                    if len(item.text.replace('Experience', '').replace('\n', '')) > 2:
                        item = item.find_elements(By.XPATH, 'div')[0] if len(
                            item.find_elements(By.XPATH, 'div')) > 0 else item
                        item = item.find_elements(By.XPATH, 'div')[0] if len(
                            item.find_elements(By.XPATH, 'div')) > 0 else item
                        experience_list = item.find_element(
                            By.XPATH, 'ul'
                        ).find_elements(
                            By.XPATH, 'li'
                        )
        for position in experience_list:
            if position.find_element(By.XPATH, 'div').get_attribute('class') == '':
                position = position.find_element(By.XPATH, 'div')
            position = position.find_element(By.XPATH, 'div')
            company_logo_elem, position_details = position.find_elements(By.XPATH, 'div')
            company_linkedin_url = company_logo_elem.find_element(By.XPATH, 'a').get_attribute('href')
            position_details_list = position_details.find_elements(By.XPATH, 'div')
            position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            position_summary_details = position_summary_details.find_element(By.XPATH, 'div')
            outer_positions = position_summary_details.find_elements(By.XPATH, '*')
            if len(outer_positions) == 4:
                position_title = outer_positions[0].find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME,
                                                                                                   "span").text
                company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                location = outer_positions[3].find_element(By.TAG_NAME, "span").text
            elif len(outer_positions) == 3:
                if "·" in outer_positions[2].text:
                    position_title = outer_positions[0].find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME,
                                                                                                       "span").text
                    company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                    work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                    location = ""
                else:
                    position_title = ""
                    company = outer_positions[0].find_element(By.TAG_NAME, "span").find_element(By.TAG_NAME,
                                                                                                "span").text
                    work_times = outer_positions[1].find_element(By.TAG_NAME, "span").text
                    location = outer_positions[2].find_element(By.TAG_NAME, "span").text
            times = work_times.split("·")[0].strip() if work_times else ""
            duration = work_times.split("·")[1].strip() if len(work_times.split("·")) > 1 else None
            from_date = " ".join(times.split(" ")[:2]) if times else ""
            to_date = " ".join(times.split(" ")[3:]) if times else ""
            if position_summary_text and len(
                    position_summary_text.find_element(
                        By.CLASS_NAME, "pvs-list").find_element(
                        By.CLASS_NAME, "pvs-list").find_elements(
                        By.XPATH, "li")) > 1:
                descriptions = position_summary_text.find_element(
                    By.CLASS_NAME, "pvs-list").find_element(
                    By.CLASS_NAME, "pvs-list").find_elements(By.XPATH, "li")
                for description in descriptions:
                    res = description.find_element(By.TAG_NAME, "a").find_elements(By.XPATH, "*")
                    position_title_elem = res[0] if len(res) > 0 else None
                    work_times_elem = res[1] if len(res) > 1 else None
                    location_elem = res[2] if len(res) > 2 else None
                    location = location_elem.find_element(By.XPATH, "*").text if location_elem else None
                    position_title = position_title_elem.find_element(
                        By.XPATH, "*").find_element(
                        By.TAG_NAME, "*").text if position_title_elem else ""
                    work_times = work_times_elem.find_element(By.XPATH, "*").text if work_times_elem else ""
                    times = work_times.split("·")[0].strip() if work_times else ""
                    duration = work_times.split("·")[1].strip() if len(work_times.split("·")) > 1 else None
                    from_date = " ".join(times.split(" ")[:2]) if times else ""
                    to_date = " ".join(times.split(" ")[3:]) if times else ""
                    experience = Experience(
                        position_title=position_title,
                        from_date=from_date,
                        to_date=to_date,
                        duration=duration,
                        location=location,
                        description=description,
                        institution_name=company,
                        linkedin_url=company_linkedin_url
                    )
                    self.add_experience(experience)
            else:
                description = position_summary_text.text if position_summary_text else ""
                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                    description=description,
                    institution_name=company,
                    linkedin_url=company_linkedin_url
                )
                self.add_experience(experience)

    def get_educations(self):
        url = os.path.join(self.linkedin_url, "details/education")
        self.driver.get(url)
        self.focus()
        main = self.wait_for_element_to_load(by=By.ID, name="main")
        self.scroll_to_half()
        self.scroll_to_bottom()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH, "//section[contains(@id,'ember')]")))
        self.wait(3)
        main_list = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions) \
            .until(expected_conditions.presence_of_all_elements_located((
            By.XPATH, "//section[contains(@id,'ember')]")))
        for item_ in main_list:
            if item_.text.startswith("Education"):
                temp_list = item_.find_elements(By.XPATH, 'div')
                for item in temp_list:
                    if len(item.text.replace('Education', '').replace('\n', '')) > 2:
                        item = item.find_elements(By.XPATH, 'div')[0] if len(
                            item.find_elements(By.XPATH, 'div')) > 0 else item
                        item = item.find_elements(By.XPATH, 'div')[0] if len(
                            item.find_elements(By.XPATH, 'div')) > 0 else item
                        education_list = item.find_element(
                            By.XPATH, 'ul'
                        ).find_elements(
                            By.XPATH, 'li'
                        )
        for position in education_list:
            if position.find_element(By.XPATH, 'div').get_attribute('class') == '':
                position = position.find_element(By.XPATH, 'div')
            position = position.find_element(By.XPATH, 'div')
            institution_logo_elem, position_details = position.find_elements(By.XPATH, 'div')
            institution_linkedin_url = institution_logo_elem.find_element(By.XPATH, "*").get_attribute("href")
            position_details_list = position_details.find_elements(By.XPATH, "*")
            position_summary_details = position_details_list[0] if len(position_details_list) > 0 else None
            position_summary_text = position_details_list[1] if len(position_details_list) > 1 else None
            outer_positions = position_summary_details.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
            institution_name = outer_positions[0].find_element(
                By.TAG_NAME, "span").find_element(By.TAG_NAME, "span").text
            degree = outer_positions[1].find_element(By.TAG_NAME, "span").text if len(outer_positions) > 1 else ""
            times = outer_positions[2].find_element(By.TAG_NAME, "span").text if len(outer_positions) > 2 else ""
            from_date = " ".join(times.split(" ")[:1])
            to_date = " ".join(times.split(" ")[2:3])
            description = position_summary_text.text if position_summary_text else ""
            education = Education(
                from_date=from_date,
                to_date=to_date,
                description=description,
                degree=degree,
                institution_name=institution_name,
                linkedin_url=institution_linkedin_url
            )
            self.add_education(education)

    def get_interest_type(self, company_list, interest: Interest, interest_type: str):
        if company_list is None:
            return
        company_list = company_list.find_element(By.XPATH, 'div').find_element(By.XPATH, 'div')
        company_list = company_list.find_element(By.XPATH, 'ul').find_elements(By.XPATH, 'li')
        for company in company_list:
            company = company.find_element(By.XPATH, 'div').find_element(By.XPATH, 'div')
            company_link, company_details = company.find_elements(By.XPATH, 'div')
            company_link = company_link.find_element(By.XPATH, 'a').get_attribute('href')
            company_details = company_details.find_element(By.XPATH, 'div')
            company_details = company_details.find_element(By.XPATH, 'a')
            name = company_details.find_element(By.XPATH, 'div').text
            if interest_type == "Top Voices":
                followers = company_details.find_elements(By.XPATH, 'span')[1].text
            else:
                followers = company_details.find_element(By.XPATH, 'span').text
            if followers:
                followers = followers.split(' ')[0].replace(',', '')
            interest_temp = InterestTemplate(
                name=name,
                url=company_link,
                followers=followers
            )
            if interest_type == "Companies":
                interest.companies.append(
                    interest_temp
                )
            elif interest_type == "Groups":
                interest.groups.append(
                    interest_temp
                )
            elif interest_type == "Schools":
                interest.schools.append(
                    interest_temp
                )
            elif interest_type == "Top Voices":
                interest.top_voices.append(
                    interest_temp
                )

    def get_interests(self):
        url = os.path.join(self.linkedin_url.split('?')[0], "details/interests/?detailScreenTabIndex=0")
        self.driver.get(url)
        self.focus()
        self.scroll_to_half()
        self.scroll_to_bottom()
        self.wait(2)
        buttons = WebDriverWait(self.driver, 10, ignored_exceptions=ignored_exceptions) \
            .until(expected_conditions.presence_of_all_elements_located((
            By.XPATH, "//button[contains(@class,'artdeco-tab')]")))
        my_buttons = []
        for button in buttons:
            if 'Companies' in button.text or 'Groups' in button.text or \
                    'Schools' in button.text or 'Top Voices' in button.text:
                my_buttons.append(button)
        data_list = self.driver.find_elements(By.CLASS_NAME, "pvs-list__container")
        interest = Interest()
        for item in data_list:
            tmp = item.find_element(By.XPATH, '..')
            self.driver.execute_script("arguments[0].setAttribute('class','artdeco-tabpanel active ember-view')", tmp)
            self.scroll_to_bottom()
            self.wait(2)
        self.get_interest_type(
            data_list[0] if 'Companies' in my_buttons[0].text else data_list[1] if 'Companies' in my_buttons[1].text
            else data_list[2] if 'Companies' in my_buttons[2].text else None,
            interest,
            'Companies'
        )
        self.get_interest_type(
            data_list[0] if 'Groups' in my_buttons[0].text else data_list[1] if 'Groups' in my_buttons[1].text
            else data_list[2] if 'Groups' in my_buttons[2].text else None,
            interest,
            'Groups'
        )
        self.get_interest_type(
            data_list[0] if 'Schools' in my_buttons[0].text else data_list[1] if 'Schools' in my_buttons[1].text
            else data_list[2] if 'Schools' in my_buttons[2].text else None,
            interest,
            'Schools'
        )
        self.get_interest_type(
            data_list[0] if 'Top Voices' in my_buttons[0].text else data_list[1] if 'Top Voices' in my_buttons[1].text
            else data_list[2] if 'Top Voices' in my_buttons[2].text else None,
            interest,
            'Top Voices'
        )
        self.add_interest(interest)

    def get_name_and_location(self):
        top_panels = self.driver.find_elements(By.CLASS_NAME, "pv-text-details__left-panel")
        self.name = top_panels[0].find_elements(By.XPATH, "*")[0].text
        self.location = top_panels[1].find_element(By.TAG_NAME, "span").text

    def get_about(self):
        about = self.driver.find_element(
            By.ID, "about").find_element(
            By.XPATH, "..").find_element(
            By.CLASS_NAME, "display-flex").text
        self.about = about

    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )
        self.focus()
        self.wait(5)
        # get name and location
        self.get_name_and_location()
        self.open_to_work = self.is_open_to_work()
        # get about
        self.get_about()
        try:
            driver.execute_script(
                "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
            )
            driver.execute_script(
                "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
            )
        except:
            pass
        # get experience
        self.get_experiences()
        # get education
        self.get_educations()
        driver.get(self.linkedin_url)
        # get interest
        self.get_interests()
        # get accomplishment
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            acc = driver.find_element(
                By.XPATH,
                "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
            )
            for block in acc.find_elements(
                    By.XPATH,
                    "//div[@class='pv-accomplishments-block__content break-words']"
            ):
                category = block.find_element(By.TAG_NAME, "h3")
                for title in block.find_element(
                        By.TAG_NAME,
                        "ul"
                ).find_elements(By.TAG_NAME, "li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    self.add_accomplishment(accomplishment)
        except:
            pass
        # get connections
        try:
            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            connections = driver.find_element(By.CLASS_NAME, "mn-connections")
            if connections is not None:
                for conn in connections.find_elements(By.CLASS_NAME, "mn-connection-card"):
                    anchor = conn.find_element(By.CLASS_NAME, "mn-connection-card__link")
                    url = anchor.get_attribute("href")
                    name = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(By.CLASS_NAME,
                                                                                                        "mn-connection-card__name").text.strip()
                    occupation = conn.find_element(By.CLASS_NAME, "mn-connection-card__details").find_element(
                        By.CLASS_NAME, "mn-connection-card__occupation").text.strip()

                    contact = Contact(name=name, occupation=occupation, url=url)
                    self.add_contact(contact)
        except:
            connections = None

        if close_on_complete:
            driver.quit()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return json.dumps({
            "name": self.name,
            "about": self.about,
            "experiences": [exp.__repr__() for exp in self.experiences],
            "educations": [edu.__repr__() for edu in self.educations],
            "interest": self.interest.__repr__(),
            "accomplishments": [acc.__repr__() for acc in self.accomplishments],
            "contacts": [con.__repr__() for con in self.contacts],
        })

