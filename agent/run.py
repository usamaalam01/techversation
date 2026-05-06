#!/usr/bin/env python3
"""
Autonomous AI blog agent.
Fetches tech/AI news, generates one MDX post per category per run (5 total).

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
from images import attribution_line, fetch_images
from scorer import rank_stories_for_category
from sources.hackernews import fetch_top_stories
from sources.rss import fetch_all_rss_feeds
from writer import inject_category, inject_cover_image, validate_mdx, write_post


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


def _run_category(
    category: dict,
    all_stories: list,
    covered: dict,
    results: list[str],
) -> None:
    """Attempt to generate one post for the given category. Mutates covered in-place."""
    cat_id = category["id"]
    cat_label = category["label"]
    print(f"\n[Run] ── Category: {cat_label} ──")

    ranked = rank_stories_for_category(
        stories=all_stories,
        category=category,
        covered_urls=covered["covered_urls"],
        covered_topics=covered["covered_topics"],
        hn_min_score=config.HN_MIN_SCORE,
    )

    if not ranked:
        print(f"[Run] {cat_label}: no eligible stories found, skipping.")
        return

    story = ranked[0]
    print(
        f"[Run] {cat_label}: selected [{story['_score']:.1f} pts] "
        f"'{story['title']}' ({story['source_name']}) → {story['_format']}"
    )

    # Fetch images — skip this category entirely if no cover image is available
    images = fetch_images(story["title"], story["source_category"], count=4)
    if not images:
        print(f"[Run] {cat_label}: no cover image found, skipping.")
        return
    cover_image = images[0]
    inline_images = images[1:]

    # Generate post (retry once on validation failure)
    mdx: str | None = None
    for attempt in range(2):
        print(f"[Run] {cat_label}: generating (attempt {attempt + 1}/2)...")
        try:
            raw = generate_post(story, inline_images=inline_images, category=cat_id)
        except RuntimeError as e:
            print(f"[Run] {cat_label}: generation failed: {e}")
            return

        if validate_mdx(raw):
            mdx = raw
            break

        print(f"[Run] {cat_label}: content failed validation, retrying...")
        time.sleep(5)

    if mdx is None:
        print(f"[Run] {cat_label}: could not generate valid post after 2 attempts, skipping.")
        return

    # Inject category + cover image into frontmatter
    mdx = inject_category(mdx, cat_id)
    if cover_image:
        mdx = inject_cover_image(mdx, cover_image["url"])
        mdx = mdx.rstrip() + f"\n\n{attribution_line(cover_image)}\n"
        print(f"[Run] {cat_label}: cover image set: {cover_image['url'][:60]}...")

    # Write MDX file
    slug = write_post(mdx, config.POSTS_DIR)

    # Mark URL + keywords as covered immediately so later categories don't reuse same story
    covered["covered_urls"].append(story["url"])
    new_keywords = _extract_keywords(story["title"])
    covered["covered_topics"] = list(set(covered["covered_topics"] + new_keywords))[-200:]
    covered["total_posts"] = covered.get("total_posts", 0) + 1

    results.append(f"content/posts/{slug}.mdx  [{cat_label}]")
    print(f"[Run] {cat_label}: ✓ draft saved → content/posts/{slug}.mdx")


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

    # ── 1. Fetch all stories once (shared across all categories) ─────────────
    print("[Run] Fetching Hacker News...")
    hn_stories = fetch_top_stories(
        limit=100,
        min_score=config.HN_MIN_SCORE,
        max_age_hours=config.MAX_AGE_HOURS,
    )

    print(f"[Run] Fetching {len(config.RSS_FEEDS)} RSS feeds...")
    rss_stories = fetch_all_rss_feeds(config.RSS_FEEDS, max_age_hours=config.MAX_AGE_HOURS)

    all_stories = hn_stories + rss_stories
    print(f"[Run] Total candidates: {len(all_stories)}")

    if not all_stories:
        print("[Run] No stories retrieved. Exiting.")
        sys.exit(0)

    # ── 2. Generate one post per category ─────────────────────────────────────
    results: list[str] = []
    for category in config.CATEGORIES:
        _run_category(category, all_stories, covered, results)

    # ── 3. Persist covered.json ────────────────────────────────────────────────
    covered["last_run"] = datetime.now(timezone.utc).isoformat()
    _save_covered(covered)

    # ── 4. Summary ────────────────────────────────────────────────────────────
    print(f"\n[Run] Done — {len(results)}/{len(config.CATEGORIES)} posts generated:")
    for r in results:
        print(f"       {r}")
    if not results:
        print("[Run] No posts generated this run.")
    print("[Run] Open Keystatic (locally) or GitHub editor to review drafts before publishing.")


if __name__ == "__main__":
    main()
