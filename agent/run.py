#!/usr/bin/env python3
"""
Autonomous AI blog agent.
Fetches tech/AI news, picks the best story, generates an MDX post, saves as draft.

Usage:
    python agent/run.py

Required env vars:
    LLM_1_API_KEY (+ LLM_1_PROVIDER, LLM_1_MODEL)
    Optionally: LLM_2_* and LLM_3_* for fallback chain
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow importing sibling modules when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import config
from generator import generate_post
from scorer import rank_stories
from sources.hackernews import fetch_top_stories
from sources.rss import fetch_all_rss_feeds
from writer import validate_mdx, write_post


def _load_covered() -> dict:
    path = Path(config.COVERED_FILE)
    if not path.exists():
        return {"covered_urls": [], "covered_topics": [], "last_run": None, "total_posts": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"covered_urls": [], "covered_topics": [], "last_run": None, "total_posts": 0}


def _save_covered(data: dict) -> None:
    path = Path(config.COVERED_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _extract_keywords(title: str) -> list[str]:
    """Pull 3 meaningful lowercase words from a title for topic dedup tracking."""
    stopwords = {
        "this", "that", "with", "from", "have", "been", "will", "what",
        "when", "where", "which", "your", "their", "about", "into", "than",
        "more", "also", "just", "over", "after", "before", "some", "these",
    }
    words = re.findall(r"\b[a-z]{4,}\b", title.lower())
    return [w for w in words if w not in stopwords][:3]


def main() -> None:
    print(f"[Run] Agent starting — {datetime.now(timezone.utc).isoformat()}")

    active_chain = [s for s in config.LLM_CHAIN if s.get("provider") and s.get("api_key")]
    if not active_chain:
        print(
            "[Run] ERROR: No LLMs configured.\n"
            "       Set at least LLM_1_PROVIDER and LLM_1_API_KEY.\n"
            "       Add them as GitHub Actions Variables/Secrets (or export locally)."
        )
        sys.exit(1)

    chain_summary = " → ".join(
        f"LLM {s['slot']} ({s['provider']}/{s['model']})" for s in active_chain
    )
    print(f"[Run] Fallback chain: {chain_summary}")

    covered = _load_covered()
    print(f"[Run] {len(covered['covered_urls'])} URLs already covered, "
          f"{covered.get('total_posts', 0)} total posts generated")

    # ── 1. Fetch stories ──────────────────────────────────────────────────────
    print("[Run] Fetching Hacker News...")
    hn_stories = fetch_top_stories(
        limit=50,
        min_score=config.HN_MIN_SCORE,
        max_age_hours=config.MAX_AGE_HOURS,
    )

    print(f"[Run] Fetching {len(config.RSS_FEEDS)} RSS feeds...")
    rss_stories = fetch_all_rss_feeds(config.RSS_FEEDS, max_age_hours=config.MAX_AGE_HOURS)

    all_stories = hn_stories + rss_stories
    print(f"[Run] Total candidates before dedup: {len(all_stories)}")

    if not all_stories:
        print("[Run] No stories retrieved from any source. Exiting.")
        sys.exit(0)

    # ── 2. Score and rank ─────────────────────────────────────────────────────
    ranked = rank_stories(
        stories=all_stories,
        covered_urls=covered["covered_urls"],
        covered_topics=covered["covered_topics"],
        max_age_hours=config.MAX_AGE_HOURS,
    )

    if not ranked:
        print("[Run] All stories already covered. Nothing new to write about.")
        sys.exit(0)

    story = ranked[0]
    print(
        f"[Run] Selected: [{story['_score']:.1f} pts] "
        f"'{story['title']}' ({story['source_name']}) → {story['_format']}"
    )

    # ── 3. Generate post (retry once on validation failure) ───────────────────
    mdx: str | None = None
    for attempt in range(2):
        print(f"[Run] Generating {story['_format']} post (attempt {attempt + 1}/2)...")
        try:
            raw = generate_post(story)
        except RuntimeError as e:
            print(f"[Run] Generation failed: {e}")
            sys.exit(1)

        if validate_mdx(raw):
            mdx = raw
            break

        print("[Run] Content failed validation, retrying with same story...")
        time.sleep(5)

    if mdx is None:
        print("[Run] Could not generate a valid post after 2 attempts. Exiting.")
        sys.exit(0)

    # ── 4. Write MDX file ─────────────────────────────────────────────────────
    slug = write_post(mdx, config.POSTS_DIR)

    # ── 5. Update covered.json ────────────────────────────────────────────────
    covered["covered_urls"].append(story["url"])
    new_keywords = _extract_keywords(story["title"])
    covered["covered_topics"] = list(set(covered["covered_topics"] + new_keywords))[-200:]
    covered["last_run"] = datetime.now(timezone.utc).isoformat()
    covered["total_posts"] = covered.get("total_posts", 0) + 1
    _save_covered(covered)

    print(f"[Run] ✓ Draft saved: content/posts/{slug}.mdx")
    print("[Run] Open Keystatic, find the post, uncheck 'Draft', and save to publish.")


if __name__ == "__main__":
    main()
