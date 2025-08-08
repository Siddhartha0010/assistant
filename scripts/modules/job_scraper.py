import os
import time
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus

JSEARCH_BASE = "https://jsearch.p.rapidapi.com/search"


def _normalize_location(loc: str) -> str:
    return loc.lower().strip()


def fetch_jobs_jsearch(
    rapidapi_key: Optional[str],
    titles: List[str],
    locations: List[str],
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """
    Fetch jobs using JSearch API on RapidAPI.
    Falls back to empty list if API key is not provided.
    """
    if not rapidapi_key:
        print("[job_scraper] RAPIDAPI_KEY not set — skipping JSearch fetch.")
        return []

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }

    jobs: List[Dict[str, Any]] = []
    titles = list(dict.fromkeys(titles))  # unique preserve order
    locations = list(dict.fromkeys(locations))

    for title in titles:
        for location in locations:
            # Construct query; JSearch supports "query" like "java developer in hyderabad"
            q = f"{title} in {location}"
            params = {
                "query": q,
                "page": "1",
                "num_pages": "1",
                "date_posted": "all",  # or last_24_hours / week
            }
            try:
                res = requests.get(JSEARCH_BASE, headers=headers, params=params, timeout=20)
                res.raise_for_status()
                data = res.json()
                result_list = data.get("data", [])
                for item in result_list:
                    jobs.append(_map_jsearch_item(item))
                time.sleep(0.6)  # be nice to the API
            except Exception as e:
                print(f"[job_scraper] JSearch fetch error for '{q}': {e}")

            if len(jobs) >= max_results:
                return jobs[:max_results]

    return jobs[:max_results]


def _map_jsearch_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map JSearch result to internal schema.
    """
    return {
        "id": item.get("job_id") or item.get("job_posted_at_timestamp") or item.get("job_title", "") + "|" + item.get("employer_name", ""),
        "title": item.get("job_title"),
        "company": item.get("employer_name"),
        "location": item.get("job_city") or item.get("job_country") or item.get("job_state") or "",
        "employment_type": item.get("job_employment_type"),
        "description": item.get("job_description") or "",
        "posted_at": item.get("job_posted_at_timestamp"),
        "remote": bool(item.get("job_is_remote")),
        "salary_min": _extract_salary(item, "min"),
        "salary_max": _extract_salary(item, "max"),
        "apply_link": _first_nonempty([
            item.get("job_apply_link"),
            item.get("job_apply_is_direct"),
            (item.get("job_apply_options") or [{}])[0].get("apply_link") if item.get("job_apply_options") else None,
        ]),
        "source": "jsearch",
        "raw": item,
    }


def _extract_salary(item: Dict[str, Any], kind: str) -> Optional[float]:
    comp = item.get("job_salary_currency")
    sal = item.get("job_salary")
    min_sal = item.get("job_min_salary")
    max_sal = item.get("job_max_salary")
    if kind == "min" and isinstance(min_sal, (int, float)):
        return float(min_sal)
    if kind == "max" and isinstance(max_sal, (int, float)):
        return float(max_sal)
    if isinstance(sal, (int, float)):
        return float(sal)
    return None


def _first_nonempty(values: List[Optional[str]]) -> Optional[str]:
    for v in values:
        if v:
            return str(v)
    return None


# Placeholders for future scrapers (LinkedIn/Naukri/Indeed/company sites)
def fetch_jobs_linkedin() -> List[Dict[str, Any]]:
    # TODO: Implement via Selenium/Playwright respecting site ToS and rate limits.
    return []


def fetch_jobs_naukri() -> List[Dict[str, Any]]:
    # TODO: Implement Naukri scraping or API when available.
    return []


def fetch_jobs_indeed() -> List[Dict[str, Any]]:
    # TODO: Implement Indeed scraping or API.
    return []
