import json

from linkedin_scraper import Person, Company, Job, JobSearch, PersonSearchScrap, actions,\
    JobSearchScrap, ExperienceLevel, OnSite, JobType
from typing import List
from urllib.parse import urljoin
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
        result_ = j.search(word)
        jobs_data.append(result_)
    j.driver.quit()
    return jobs_data


class RequestModelSearchPerson:
    first_name: str
    last_name: str or None


def search_persons_data(search_data: List[dict]):
    results = []
    j = PersonSearchScrap(close_on_complete=True)
    for item in search_data:
        result_data = j.search(first_name=item["first_name"], last_name=item["last_name"],
                               location=item["location"], keywords=item["keywords"], limit=item["limit"])
        if result_data is not None:
            results.append({
                "first_name": item["first_name"],
                "last_name": item["last_name"],
                "location": item["location"],
                "keywords": item["keywords"],
                "limit": len(result_data),
                "results": result_data
            })
    return results


def search_jobs_data(search_data: List[dict]):
    results = []
    j = JobSearchScrap(close_on_complete=True)
    for item in search_data:
        result_data = j.search(
            keywords=item.get("keywords", None),
            location=item.get("location", None),
            refresh=item.get("refresh", True),
            past_date_seconds=item.get("past_date_seconds", None),
            experience_level=item.get("experience_level", None),
            company_name=item.get("company_name", None),
            job_type=item.get("job_type", None),
            on_site=item.get("on_site", None),
            limit=item.get("limit", None)
        )

        if result_data is not None:
            item.update({
                "limit": len(result_data),
                "results": result_data
            })
            results.append(item)
    return results


search_keywords = [
    {
        "keywords": "python developer",
        "location": "Lahore, Punjab, Pakistan",
        "refresh": None,
        "past_date_seconds": 2592000,
        "experience_level": [ExperienceLevel.entry_level, ExperienceLevel.mid_senior_level],
        "company_name": ["Turing"],
        "job_type": [JobType.full_time, JobType.part_time],
        "on_site": [OnSite.on_site, OnSite.remote],
        "limit": 100
    }
]
result = search_jobs_data(search_keywords)

print("OK")
