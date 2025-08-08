import json
import os
import re
from typing import Any, Dict, List, Tuple
from collections import defaultdict


def normalize_text(s: str) -> str:
    return (s or "").lower().strip()


def compute_skill_match(job: Dict[str, Any], skills: List[str]) -> int:
    """
    Simple heuristic: count skill keyword hits in title + description + employment type.
    """
    text = " ".join([
        normalize_text(job.get("title", "")),
        normalize_text(job.get("description", "")),
        normalize_text(job.get("employment_type", "")),
    ])

    hits = 0
    for skill in skills:
        # allow word boundary-ish match for single words, substring for phrases
        sk = normalize_text(skill)
        if " " in sk:
            if sk in text:
                hits += 1
        else:
            if re.search(rf"(^|\W){re.escape(sk)}(\W|$)", text):
                hits += 1

    return int(100 * hits / max(1, len(skills)))


def location_ok(job: Dict[str, Any], onsite_cities_allowed: List[str], locations_allowed: List[str]) -> bool:
    loc = normalize_text(job.get("location", ""))

    if not loc:
        # If unknown, allow; filtering primarily on skills and title
        return True

    # Remote friendly
    if "remote" in loc:
        return True

    # Check allowed locations
    for allowed in locations_allowed:
        if normalize_text(allowed) in loc:
            return True

    # Onsite restriction: only allowed cities for onsite roles
    title_desc = normalize_text(job.get("title", "")) + " " + normalize_text(job.get("description", ""))
    if any(city in loc for city in onsite_cities_allowed):
        return True

    return False


def salary_ok(job: Dict[str, Any], min_lpa: float, max_lpa: float) -> bool:
    """
    Attempt to interpret salary on LPA scale.
    If salary info is missing, we allow it (many fresher jobs omit salary).
    """
    min_sal = job.get("salary_min")
    max_sal = job.get("salary_max")

    # If salary present and clearly outside bounds, reject
    if min_sal is not None and (min_sal / 100000.0) > max_lpa:
        return False
    if max_sal is not None and (max_sal / 100000.0) < min_lpa:
        return True  # if max < min_lpa, it's probably unspecified; allow

    return True


def experience_ok(job: Dict[str, Any], exp_levels: List[str]) -> bool:
    text = normalize_text(job.get("title", "")) + " " + normalize_text(job.get("description", ""))
    for tag in exp_levels:
        if normalize_text(tag) in text:
            return True
    # If description doesn't mention, don't exclude
    return True


def title_ok(job: Dict[str, Any], titles: List[str]) -> bool:
    title = normalize_text(job.get("title", ""))
    if not title:
        return True
    for t in titles:
        if normalize_text(t) in title:
            return True
    return False


def score_and_filter_jobs(
    jobs: List[Dict[str, Any]],
    titles: List[str],
    skills: List[str],
    onsite_cities_allowed: List[str],
    locations_allowed: List[str],
    min_lpa: float,
    max_lpa: float,
    exp_levels: List[str],
    min_skill_match_to_include: int,
) -> List[Dict[str, Any]]:
    """
    Apply all filters and add 'match_score' to each job.
    """
    filtered: List[Dict[str, Any]] = []
    for j in jobs:
        if not title_ok(j, titles):
            continue
        if not location_ok(j, onsite_cities_allowed, locations_allowed):
            continue
        if not salary_ok(j, min_lpa, max_lpa):
            continue
        if not experience_ok(j, exp_levels):
            continue
        score = compute_skill_match(j, skills)
        if score < min_skill_match_to_include:
            continue
        j["match_score"] = score
        filtered.append(j)

    # Sort by score desc, then title
    filtered.sort(key=lambda x: (x.get("match_score", 0), x.get("title", "")), reverse=True)
    return filtered


def dedupe_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for j in jobs:
        key = j.get("id") or (j.get("title", "") + "|" + j.get("company", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out
