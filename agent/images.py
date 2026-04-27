"""
Unsplash image fetching for blog posts.
Requires UNSPLASH_ACCESS_KEY env var (free at unsplash.com/developers).
Gracefully returns empty list if key is missing or API fails.
"""
import re
from typing import Any

import httpx

import config

_UNSPLASH_SEARCH = "https://api.unsplash.com/search/photos"

_CATEGORY_HINTS = {
    "ai_blog":    "artificial intelligence machine learning",
    "arxiv":      "science research data",
    "hackernews": "technology software",
    "tech_news":  "technology digital innovation",
}

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "must", "can", "to", "of", "in", "on", "at", "by", "for", "with",
    "about", "as", "into", "through", "why", "how", "what", "when", "where",
    "this", "that", "and", "but", "or", "its", "your", "their", "our",
}


def _build_query(title: str, category: str) -> str:
    words = re.findall(r"\b[a-zA-Z]{3,}\b", title)
    keywords = [w for w in words if w.lower() not in _STOPWORDS][:5]
    hint = _CATEGORY_HINTS.get(category, "technology")
    query = " ".join(keywords) + " " + hint
    return query.strip()[:100]


def fetch_images(title: str, category: str, count: int = 4) -> list[dict[str, Any]]:
    """
    Search Unsplash and return up to `count` image dicts.
    Each dict has: url, alt, photographer, photographer_url, unsplash_url.
    Returns [] if key not configured or search fails.
    """
    if not config.UNSPLASH_ACCESS_KEY:
        print("[Images] UNSPLASH_ACCESS_KEY not set — skipping images")
        return []

    query = _build_query(title, category)
    print(f"[Images] Searching Unsplash: '{query}'")

    try:
        r = httpx.get(
            _UNSPLASH_SEARCH,
            params={
                "query": query,
                "client_id": config.UNSPLASH_ACCESS_KEY,
                "per_page": count,
                "orientation": "landscape",
                "content_filter": "high",
            },
            timeout=10,
            headers={"Accept-Version": "v1"},
        )
        r.raise_for_status()
        results = r.json().get("results", [])
    except Exception as e:
        print(f"[Images] Unsplash request failed: {e}")
        return []

    images = []
    for photo in results:
        utm = "?utm_source=techversation&utm_medium=referral"
        images.append({
            "url": photo["urls"]["regular"],
            "alt": (photo.get("alt_description") or query).strip()[:120],
            "photographer": photo["user"]["name"],
            "photographer_url": photo["user"]["links"]["html"] + utm,
            "unsplash_url": photo["links"]["html"] + utm,
        })

    print(f"[Images] Found {len(images)} image(s)")
    return images


def attribution_line(image: dict[str, Any]) -> str:
    """Return a markdown attribution line for an Unsplash photo."""
    return (
        f"*Photo by [{image['photographer']}]({image['photographer_url']}) "
        f"on [Unsplash]({image['unsplash_url']})*"
    )
