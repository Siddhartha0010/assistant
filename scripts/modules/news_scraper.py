from typing import List, Dict, Any
import feedparser
from urllib.parse import quote_plus


def fetch_google_news_rss(topics: List[str], limit_per_topic: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch Google News RSS for given topics.
    """
    articles: List[Dict[str, Any]] = []
    for topic in topics:
        query = quote_plus(topic)
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit_per_topic]:
                articles.append({
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "published": entry.get("published"),
                    "source": "google_news",
                    "topic": topic,
                })
        except Exception as e:
            print(f"[news_scraper] RSS error for '{topic}': {e}")
    return articles


# Placeholders for official govt/bank sources
def fetch_govt_jobs_news() -> List[Dict[str, Any]]:
    # TODO: Add Employment News / state portals scraping
    return []


def fetch_bank_jobs_news() -> List[Dict[str, Any]]:
    # TODO: Add IBPS/SBI/RBI announcements via RSS or scraping
    return []
