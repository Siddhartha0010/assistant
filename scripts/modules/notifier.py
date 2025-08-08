import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional
import requests


def build_digest_text(jobs: List[Dict[str, Any]], news: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("📢 Daily Job & News Update")
    lines.append("")
    if jobs:
        lines.append(f"💼 Jobs ({len(jobs)}):")
        for i, j in enumerate(jobs, start=1):
            title = j.get("title") or "Unknown Title"
            company = j.get("company") or "Unknown Company"
            loc = j.get("location") or "Location N/A"
            score = j.get("match_score", 0)
            sal = ""
            if j.get("salary_min") or j.get("salary_max"):
                sal = f" | Salary: {j.get('salary_min')} - {j.get('salary_max')}"
            link = j.get("apply_link") or "N/A"
            lines.append(f"{i}. {title} — {company} — {loc} — Match {score}% — {link}")
    else:
        lines.append("💼 Jobs: No matches today.")

    lines.append("")
    if news:
        lines.append(f"📰 News ({len(news)}):")
        for i, n in enumerate(news, start=1):
            title = n.get("title") or "Untitled"
            link = n.get("link") or "#"
            topic = n.get("topic") or ""
            lines.append(f"{i}. {title} [{topic}] — {link}")
    else:
        lines.append("📰 News: No items today.")
    return "\n".join(lines)


def build_digest_html(jobs: List[Dict[str, Any]], news: List[Dict[str, Any]]) -> str:
    def esc(s: Optional[str]) -> str:
        if not s:
            return ""
        return (s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))

    job_rows = []
    for j in jobs:
        job_rows.append(
            f"<li><strong>{esc(j.get('title'))}</strong> — {esc(j.get('company'))} — {esc(j.get('location'))} "
            f"(Match {j.get('match_score', 0)}%) "
            f"- <a href='{esc(j.get('apply_link') or '#')}' target='_blank' rel='noreferrer'>Apply</a></li>"
        )

    news_rows = []
    for n in news:
        news_rows.append(
            f"<li><a href='{esc(n.get('link') or '#')}' target='_blank' rel='noreferrer'>{esc(n.get('title'))}</a>"
            f" <em>({esc(n.get('topic'))})</em></li>"
        )

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color:#111;">
        <h2>📢 Daily Job & News Update</h2>
        <h3>💼 Jobs ({len(jobs)})</h3>
        <ul>
          {''.join(job_rows) if job_rows else '<li>No matches today.</li>'}
        </ul>
        <h3>📰 News ({len(news)})</h3>
        <ul>
          {''.join(news_rows) if news_rows else '<li>No items today.</li>'}
        </ul>
        <p style="margin-top:24px;color:#666;font-size:12px">This is an automated digest.</p>
      </body>
    </html>
    """
    return html


def send_whatsapp_via_twilio(
    account_sid: Optional[str],
    auth_token: Optional[str],
    from_whatsapp: Optional[str],
    to_whatsapp: Optional[str],
    body: str,
) -> bool:
    if not (account_sid and auth_token and from_whatsapp and to_whatsapp):
        print("[notifier] Missing Twilio WhatsApp env vars — printing to console instead.\n")
        print(body)
        return False

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": from_whatsapp,
        "To": to_whatsapp,
        "Body": body,
    }

    try:
        resp = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=20)
        if resp.status_code >= 200 and resp.status_code < 300:
            print("[notifier] WhatsApp sent via Twilio.")
            return True
        print(f"[notifier] Twilio error {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        print(f"[notifier] Twilio request failed: {e}")
        return False


def send_email_via_gmail(
    smtp_user: Optional[str],
    app_password: Optional[str],
    to_email: Optional[str],
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    if not (smtp_user and app_password and to_email):
        print("[notifier] Missing Gmail SMTP env vars — printing to console instead.\n")
        print(text_body or "")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_user, app_password)
            server.sendmail(smtp_user, [to_email], msg.as_string())
        print("[notifier] Email sent via Gmail SMTP.")
        return True
    except Exception as e:
        print(f"[notifier] SMTP error: {e}")
        return False
