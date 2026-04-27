import calendar
import re
import time
from datetime import datetime, timezone
from typing import Any

import feedparser


def _parse_date(entry: Any) -> datetime:
    """Extract a timezone-aware datetime from a feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            return datetime.fromtimestamp(calendar.timegm(val), tz=timezone.utc)
    return datetime.now(timezone.utc)


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_rss_feed(
    feed_config: dict[str, str],
    max_age_hours: int = 48,
) -> list[dict[str, Any]]:
    """Fetch and parse a single RSS/Atom feed."""
    url = feed_config["url"]
    name = feed_config["name"]
    category = feed_config["category"]

    try:
        parsed = feedparser.parse(url, agent="TechBlogAgent/1.0")

        if parsed.get("bozo") and not parsed.get("entries"):
            print(f"[RSS] {name}: parse error — {parsed.get('bozo_exception', 'unknown')}")
            return []

        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
        stories = []

        for entry in parsed.entries:
            pub_date = _parse_date(entry)
            if pub_date.timestamp() < cutoff:
                continue

            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue

            raw_summary = entry.get("summary") or entry.get("description") or ""
            summary = _strip_html(raw_summary)[:400] if raw_summary else ""

            stories.append({
                "title": title,
                "url": link,
                "score": 0,
                "published": pub_date.isoformat(),
                "source_name": name,
                "source_category": category,
                "description": summary,
            })

        print(f"[RSS] {name}: {len(stories)} stories within {max_age_hours}h")
        return stories

    except Exception as e:
        print(f"[RSS] {name}: failed — {e}")
        return []


def fetch_all_rss_feeds(
    feed_configs: list[dict],
    max_age_hours: int = 48,
) -> list[dict[str, Any]]:
    """Fetch all configured RSS feeds with polite 1-second delays."""
    all_stories: list[dict[str, Any]] = []
    for feed_config in feed_configs:
        stories = fetch_rss_feed(feed_config, max_age_hours)
        all_stories.extend(stories)
        time.sleep(1)
    return all_stories
