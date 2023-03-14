import json

from linkedin_scraper import Person, Company, Job, JobSearch
from typing import List
import pandas as pd

import json
import csv


def get_person_data(linkedin_url: str):
    p = Person(linkedin_url=linkedin_url, close_on_complete=True)
    person_data = p.__repr__()
    return person_data


def get_persons_data(linkedin_urls: List[str]):
    persons_data = []
    for linkedin_url in linkedin_urls:
        p = Person(linkedin_url=linkedin_url, close_on_complete=True)
        persons_data.append(p.__repr__())
    return persons_data


def get_company_data(linkedin_url: str):
    c = Company(linkedin_url=linkedin_url, close_on_complete=True)
    company_data = c.__repr__()
    return company_data


def get_companies_data(linkedin_urls: List[str]):
    companies_data = []
    for linkedin_url in linkedin_urls:
        c = Company(linkedin_url=linkedin_url, close_on_complete=True)
        companies_data.append(c.__repr__())
    return companies_data


def get_job_data(linkedin_url: str):
    j = Job(linkedin_url=linkedin_url, close_on_complete=True)
    job_data = j.__repr__()
    return job_data


def get_jobs_data(linkedin_urls: List[str]):
    jobs_data = []
    for linkedin_url in linkedin_urls:
        j = Job(linkedin_url=linkedin_url, close_on_complete=True)
        jobs_data.append(j.__repr__())
    return jobs_data


def get_job_search_data():
    j = JobSearch(close_on_complete=True, scrape=True)
    job_data = j.__repr__()
    return job_data


def get_job_searches_data(keywords: List[str]):
    jobs_data = []
    j = JobSearch(close_on_complete=False, scrape=False)
    for word in keywords:
        result = j.search(word)
        jobs_data.append(result)
    j.driver.quit()

    with open('get_job_searches_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'age', 'subject_name', 'subject_marks'])

    df = pd.read_json(json.dumps(jobs_data))
    df.to_csv("get_job_searches_data.csv")
    return jobs_data


results = get_job_searches_data(["computer Science", "Math Master"])
