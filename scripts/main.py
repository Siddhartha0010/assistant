import argparse
import json
import os
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
import pytz

from config.config import Preferences, Secrets
from modules.job_scraper import fetch_jobs_jsearch
from modules.news_scraper import fetch_google_news_rss
from modules.filter import score_and_filter_jobs, dedupe_jobs
from modules.notifier import build_digest_text, build_digest_html, send_whatsapp_via_twilio, send_email_via_gmail


def ensure_data_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_cache(cache_path: str, jobs: List[Dict[str, Any]]):
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"ts": datetime.utcnow().isoformat(), "ids": [j.get("id") for j in jobs]}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[main] Failed to save cache: {e}")


def load_cache(cache_path: str) -> List[str]:
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("ids", [])
    except Exception:
        return []


def filter_out_previous(jobs: List[Dict[str, Any]], seen_ids: List[str]) -> List[Dict[str, Any]]:
    seen = set(seen_ids or [])
    out = []
    for j in jobs:
        jid = j.get("id")
        key = jid or (j.get("title", "") + "|" + j.get("company", ""))
        if key in seen:
            continue
        out.append(j)
    return out


def run_once():
    prefs = Preferences()
    secrets = Secrets()

    ensure_data_dir(prefs.data_dir)

    # 1) Fetch jobs
    all_jobs: List[Dict[str, Any]] = []
    all_jobs += fetch_jobs_jsearch(
        rapidapi_key=secrets.rapidapi_key,
        titles=prefs.titles,
        locations=prefs.locations_allowed,
        max_results=100,
    )
    # Future: add LinkedIn/Naukri/Indeed/company fetchers

    # 2) Dedupe and filter
    all_jobs = dedupe_jobs(all_jobs)
    # Remove previously seen (today’s digest should be fresh; optional)
    seen_ids = load_cache(prefs.cache_file)
    unseen_jobs = filter_out_previous(all_jobs, seen_ids)

    filtered_jobs = score_and_filter_jobs(
        jobs=unseen_jobs,
        titles=prefs.titles,
        skills=prefs.skills,
        onsite_cities_allowed=prefs.onsite_cities_allowed,
        locations_allowed=prefs.locations_allowed,
        min_lpa=prefs.min_salary_lpa,
        max_lpa=prefs.max_salary_lpa,
        exp_levels=prefs.experience_levels,
        min_skill_match_to_include=prefs.min_skill_match_percent_to_include,
    )
    filtered_jobs = filtered_jobs[: prefs.max_jobs_in_digest]

    # 3) Fetch news
    news = fetch_google_news_rss(prefs.news_topics, limit_per_topic=2)
    news = news[: prefs.max_news_in_digest]

    # 4) Build digest
    text_digest = build_digest_text(filtered_jobs, news)
    html_digest = build_digest_html(filtered_jobs, news)
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d %b %Y")
    subject = f"Daily Jobs & News Digest — {today}"

    # 5) Notify
    if prefs.send_whatsapp:
        send_whatsapp_via_twilio(
            account_sid=secrets.twilio_account_sid,
            auth_token=secrets.twilio_auth_token,
            from_whatsapp=secrets.twilio_whatsapp_from,
            to_whatsapp=secrets.whatsapp_to,
            body=text_digest,
        )
    if prefs.send_email:
        send_email_via_gmail(
            smtp_user=secrets.smtp_user,
            app_password=secrets.smtp_app_password,
            to_email=secrets.email_to,
            subject=subject,
            html_body=html_digest,
            text_body=text_digest,
        )

    # 6) Save cache to avoid duplicates next runs
    save_cache(prefs.cache_file, filtered_jobs)


def main():
    load_dotenv()  # load env if provided by runtime
    parser = argparse.ArgumentParser(description="AI Job & News Assistant — Phase 1")
    parser.add_argument("--once", action="store_true", help="Run once immediately (default).")
    args = parser.parse_args()

    # For Phase 1 in this environment, we run once.
    run_once()


if __name__ == "__main__":
    main()
