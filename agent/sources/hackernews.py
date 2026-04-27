import time
from datetime import datetime, timezone
from typing import Any

import httpx

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def fetch_top_stories(
    limit: int = 50,
    min_score: int = 100,
    max_age_hours: int = 48,
) -> list[dict[str, Any]]:
    """Fetch top HN stories filtered by score and age."""
    try:
        response = httpx.get(HN_TOP_URL, timeout=10)
        response.raise_for_status()
        story_ids = response.json()[:200]
    except Exception as e:
        print(f"[HN] Failed to fetch top stories list: {e}")
        return []

    now = datetime.now(timezone.utc).timestamp()
    cutoff = now - (max_age_hours * 3600)
    stories = []

    for story_id in story_ids:
        if len(stories) >= limit:
            break
        try:
            r = httpx.get(HN_ITEM_URL.format(story_id), timeout=10)
            r.raise_for_status()
            item = r.json()

            if item.get("type") != "story":
                continue
            if not item.get("url"):
                continue
            if item.get("score", 0) < min_score:
                continue
            if item.get("time", 0) < cutoff:
                continue

            stories.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "score": item.get("score", 0),
                "published": datetime.fromtimestamp(item["time"], tz=timezone.utc).isoformat(),
                "source_name": "Hacker News",
                "source_category": "hackernews",
                "description": "",
            })
            time.sleep(0.1)
        except Exception as e:
            print(f"[HN] Failed to fetch item {story_id}: {e}")
            continue

    print(f"[HN] {len(stories)} qualifying stories found")
    return stories
