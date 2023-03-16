class ExperienceLevel:
    internship = "Internship"
    entry_level = "Entry Level"
    associate = "Associate"
    mid_senior_level = "Mid-Senior Level"
    director = "Director"
    executive = "Executive"


def get_experience_level(experience_level: str) -> int or None:
    data = {
        "Internship": 1,
        "Entry Level": 2,
        "Associate": 3,
        "Mid-Senior Level": 4,
        "Director": 5,
        "Executive": 6
    }
    return data.get(experience_level, None)


class JobType:
    full_time = "Full-time"
    part_time = "Part-time"
    contract = "Contract"


def get_job_type(job_type: str) -> str or None:
    data = {
        "Full-time": "F",
        "Part-time": "P",
        "Contract": "C"
    }
    return data.get(job_type, None)


class OnSite:
    on_site = "On-site"
    remote = "Remote"
    hybrid = "Hybrid"


def get_on_site(on_site: str) -> int or None:
    data = {
        "On-site": 1,
        "Remote": 2,
        "Hybrid": 3
    }
    return data.get(on_site, None)

