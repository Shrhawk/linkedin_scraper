import requests


def get_company_ids_by_name_search(name: str):
    data = requests.get("https://www.linkedin.com/jobs-guest/api/typeaheadHits", params={
        "typeaheadType": "COMPANY",
        "query": name
    })
    if data.status_code == 200:
        return data.json()
    else:
        return []


def get_geo_location_ids_by_name_search(name: str):
    data = requests.get("https://www.linkedin.com/jobs-guest/api/typeaheadHits", params={
        "typeaheadType": "GEO",
        "query": name,
        "geoTypes": "POPULATED_PLACE,ADMIN_DIVISION_2,MARKET_AREA,COUNTRY_REGION"
    })
    if data.status_code == 200:
        return data.json()
    else:
        return []

