import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Preferences:
    # User profile
    name: str = "You"
    graduation_month_year: str = "March 2026"
    cgpa: float = 7.69
    internships: List[str] = field(default_factory=lambda: ["HCCB", "CYIENT"])

    # Job preferences
    titles: List[str] = field(
        default_factory=lambda: [
            "software developer",
            "java developer",
            "web developer",
            "full stack developer",
            "backend developer",
            "frontend developer",
            "graduate engineer trainee",
            "software engineer",
            "sde",
            "sde 1",
            "fresher",
            "junior developer",
            "intern",
        ]
    )
    skills: List[str] = field(default_factory=lambda: ["java", "web development", "javascript", "react", "node", "dsa", "html", "css", "sql"])
    min_salary_lpa: float = 3.0
    max_salary_lpa: float = 50.0
    experience_levels: List[str] = field(default_factory=lambda: ["fresher", "graduate", "entry level", "junior", "intern"])
    work_types: List[str] = field(default_factory=lambda: ["onsite", "remote", "hybrid"])
    onsite_cities_allowed: List[str] = field(default_factory=lambda: ["hyderabad"])
    locations_allowed: List[str] = field(default_factory=lambda: [
        "hyderabad, telangana, india",
        "visakhapatnam, andhra pradesh, india",
        "visakhapatnam",
        "vizag",
        "hyderabad",
        "remote",
        "india",
    ])
    min_skill_match_percent_to_include: int = 0  # show everything in digest
    min_skill_match_percent_to_auto_apply: int = 50  # used in Phase 2

    # News preferences
    news_topics: List[str] = field(default_factory=lambda: [
        "IT jobs India",
        "Government jobs India",
        "Bank recruitment India",
        "Software hiring India",
        "Freshers hiring India",
        "Campus placements India",
        "Hyderabad IT jobs",
        "Visakhapatnam IT jobs",
    ])

    # Delivery preferences
    send_whatsapp: bool = True
    send_email: bool = True
    digest_hour_ist: int = 8
    digest_minute_ist: int = 0

    # Limits
    max_jobs_in_digest: int = 20
    max_news_in_digest: int = 10

    # Data paths
    data_dir: str = "scripts/data"
    cache_file: str = "scripts/data/job_cache.json"


@dataclass
class Secrets:
    # Jobs API
    rapidapi_key: Optional[str] = os.getenv("RAPIDAPI_KEY")  # for JSearch

    # WhatsApp via Twilio
    twilio_account_sid: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_whatsapp_from: Optional[str] = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g., 'whatsapp:+14155238886'
    whatsapp_to: Optional[str] = os.getenv("WHATSAPP_TO")  # e.g., 'whatsapp:+91XXXXXXXXXX'

    # Email (Gmail SMTP)
    smtp_user: Optional[str] = os.getenv("SMTP_GMAIL_USER")  # your@gmail.com
    smtp_app_password: Optional[str] = os.getenv("SMTP_GMAIL_APP_PASSWORD")  # app password
    email_to: Optional[str] = os.getenv("EMAIL_TO")  # destination email
