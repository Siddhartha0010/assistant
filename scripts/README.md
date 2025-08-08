# AI Job & News Assistant — Phase 1 (Jobs + News + Notifications)

This is the Phase 1 implementation that:
- Fetches fresher-friendly software developer jobs (Java, Web, DSA) with India‑specific constraints.
- Fetches IT/Govt/Bank related news via Google News RSS.
- Applies filters (skills, location, salary, experience).
- Sends a daily digest via WhatsApp (Twilio) and Email (Gmail SMTP).
- Prints to console if credentials are missing.

Later phases will add auto-apply (Selenium/Playwright), LinkedIn/Naukri scrapers, history DB, and voice interface.

## Quick Start

1) Ensure Python 3.11+ installed.

2) Install dependencies:
\`\`\`
pip install -r scripts/requirements.txt
\`\`\`

3) Set environment variables (at least for delivery):
- JSearch (RapidAPI) — for jobs API:
  - RAPIDAPI_KEY=<your_rapidapi_key>

- WhatsApp via Twilio (optional now; falls back to console):
  - TWILIO_ACCOUNT_SID=<sid>
  - TWILIO_AUTH_TOKEN=<token>
  - TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  (Twilio sandbox or your number)
  - WHATSAPP_TO=whatsapp:+91XXXXXXXXXX

- Email via Gmail SMTP (optional now; falls back to console):
  - SMTP_GMAIL_USER=your@gmail.com
  - SMTP_GMAIL_APP_PASSWORD=your_app_password
  - EMAIL_TO=destination@example.com

4) Run once locally:
\`\`\`
python scripts/main.py --once
\`\`\`

You should see a compiled digest in your console if credentials are missing; otherwise you’ll receive it on WhatsApp and/or Email.

## Preferences (already set to your profile)

- Roles: Software Developer, Java Developer, Web Developer, SDE, Fresher, etc.
- Skills: Java, Web Development, JavaScript, React, Node, DSA, HTML, CSS, SQL.
- Locations: Hyderabad, Visakhapatnam (Vizag), Remote, India.
- Onsite: Allowed only in Hyderabad.
- Salary: ₹3 LPA to ₹50 LPA (heuristic; many fresher roles don’t state salary).
- Experience: Fresher/Graduate/Entry/Junior/Intern.
- News topics: IT jobs, Govt jobs, Bank recruitment, Hyderabad/Vizag IT jobs.

You can edit these in `scripts/config/config.py` (Preferences dataclass).

## Scheduling (8 AM IST)

For production, use a cloud scheduler (AWS CloudWatch, GCP Scheduler, or any cron) to call this script at 08:00 Asia/Kolkata daily.

Example cron (server time UTC; 8AM IST = 02:30 UTC during standard time):
\`\`\`
30 2 * * * /usr/bin/python /path/to/scripts/main.py --once
\`\`\`

Adjust for DST/IST as needed.

## Extending to Phase 2+

- Auto-Apply:
  - Add `scripts/modules/auto_apply.py` with Selenium/Playwright flows for LinkedIn/Naukri/Indeed.
  - Store applied jobs in a DB (SQLite/MongoDB) to avoid re-applying.

- Smarter Matching:
  - Replace keyword match with a semantic scorer (e.g., small local model or API).
  - Add resume parsing to compare job requirements vs your CV.

- More Sources:
  - Implement `fetch_jobs_linkedin`, `fetch_jobs_naukri`, and `fetch_jobs_indeed` respecting ToS.
  - Add official govt/bank RSS/scrapers in `news_scraper.py`.

- Voice:
  - A small webhook/bot to request “today’s jobs” on demand + TTS reply.

## Notes

- Many fresher roles don’t publish salary; the filter permits missing salary.
- Be mindful of terms of service and rate limits when adding scrapers.
- Keep credentials secure (cloud secret manager or env vars).

## Troubleshooting

- No WhatsApp or Email arrived:
  - Ensure env vars are set.
  - For Twilio WhatsApp sandbox, join the sandbox and use the sandbox number.
  - For Gmail SMTP, you need an App Password on accounts with 2FA enabled.

- Empty results:
  - Provide `RAPIDAPI_KEY`.
  - Try running during weekdays/mornings; openings vary by time.
  - Expand titles/locations in `config.py`.
