import requests


def get_company_ids_by_name_search(name: str):
    return requests.get("https://www.linkedin.com/jobs-guest/api/typeaheadHits", params={
        "typeaheadType": "COMPANY",
        "query": name
    }).json()


def get_geo_location_ids_by_name_search(name: str):
    return requests.get("https://www.linkedin.com/jobs-guest/api/typeaheadHits", params={
        "typeaheadType": "GEO",
        "query": name,
        "geoTypes": "POPULATED_PLACE,ADMIN_DIVISION_2,MARKET_AREA,COUNTRY_REGION"
    }).json()

