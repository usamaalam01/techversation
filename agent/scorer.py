import re
from datetime import datetime, timezone
from typing import Any

import config

_TUTORIAL_RE = re.compile(
    r"\b(releases?|launched?|announces?|announcing|new model|new api|v\d+\.\d+"
    r"|open[- ]?source[sd]?|available now|introduces?|unveiled?|open[- ]?weight)\b",
    re.IGNORECASE,
)


def _recency_score(published_iso: str, max_age_hours: int) -> float:
    """0–40 pts, linear decay from now to max_age_hours ago."""
    try:
        pub = datetime.fromisoformat(published_iso)
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - pub).total_seconds() / 3600
        ratio = max(0.0, 1.0 - age_h / max(max_age_hours, 1))
        return round(ratio * 40, 2)
    except Exception:
        return 0.0


def _engagement_score(story: dict[str, Any]) -> float:
    """0–30 pts. HN uses upvotes; RSS sources get a flat 15."""
    if story["source_category"] == "hackernews":
        return min(story.get("score", 0) / 500 * 30, 30.0)
    return 15.0


def _novelty_bonus(story: dict[str, Any], covered_topics: list[str]) -> int:
    """+10 if no covered topic keyword appears in the story title."""
    title_lower = story["title"].lower()
    for topic in covered_topics:
        if topic and topic.lower() in title_lower:
            return 0
    return 10


def classify_format(story: dict[str, Any]) -> str:
    """Return 'explainer', 'tutorial', or 'analysis' based on source/title."""
    if story["source_category"] == "arxiv":
        return "explainer"
    if _TUTORIAL_RE.search(story["title"]):
        return "tutorial"
    return "analysis"


def rank_stories(
    stories: list[dict[str, Any]],
    covered_urls: list[str],
    covered_topics: list[str],
    max_age_hours: int,
) -> list[dict[str, Any]]:
    """Remove already-covered stories, score remaining ones, sort descending."""
    covered_set = set(covered_urls)
    unique = [s for s in stories if s["url"] not in covered_set]

    for story in unique:
        story["_score"] = (
            _recency_score(story["published"], max_age_hours)
            + _engagement_score(story)
            + config.SOURCE_WEIGHTS.get(story["source_category"], 10)
            + _novelty_bonus(story, covered_topics)
        )
        story["_format"] = classify_format(story)

    return sorted(unique, key=lambda s: s["_score"], reverse=True)
