import os

# GitHub Actions doesn't allow empty secret values, so placeholders like "-"
# are used instead. This helper normalises them all to an empty string.
_PLACEHOLDERS = {"-", "none", "null", "n/a", "na", "placeholder", "undefined"}

def _env(key: str, default: str = "") -> str:
    val = os.environ.get(key, default).strip()
    return "" if val.lower() in _PLACEHOLDERS else val


MAX_AGE_HOURS = int(os.environ.get("MAX_AGE_HOURS", "48"))
HN_MIN_SCORE = int(os.environ.get("HN_MIN_SCORE", "100"))

# ── Per-category publishing config ────────────────────────────────────────────
# Each run generates one post per category (5 total).
# source_categories: which RSS/HN source groups to pull from for this category
# require_release_keywords: only pick stories that sound like product launches
# min_score: override HN_MIN_SCORE for this category (None = use default)
# age_hours: override MAX_AGE_HOURS for this category (None = use default)
# format: force a specific post format; None = auto-detect per classify_format()
CATEGORIES = [
    {
        "id": "news",
        "label": "News",
        "source_categories": ["tech_news", "hackernews"],
        "require_release_keywords": False,
        "min_score": None,
        "age_hours": 24,
        "format": "analysis",
    },
    {
        "id": "articles",
        "label": "Articles",
        "source_categories": ["ai_blog"],
        "require_release_keywords": False,
        "min_score": None,
        "age_hours": 48,
        "format": None,  # auto-detect: analysis or tutorial
    },
    {
        "id": "tools",
        "label": "Tools",
        "source_categories": ["ai_blog", "tech_news", "hackernews"],
        "require_release_keywords": True,
        "min_score": None,
        "age_hours": 48,
        "format": "tutorial",
    },
    {
        "id": "trending",
        "label": "Trending",
        "source_categories": ["hackernews"],
        "require_release_keywords": False,
        "min_score": 200,  # higher bar — only truly hot stories
        "age_hours": 24,
        "format": "analysis",
    },
    {
        "id": "tutorials",
        "label": "Tutorials",
        "source_categories": ["arxiv", "ai_blog"],
        "require_release_keywords": False,
        "min_score": None,
        "age_hours": 48,
        "format": "tutorial",
    },
]

# ── LLM fallback chain ────────────────────────────────────────────────────────
# The agent tries LLM_1 first. On any failure (quota, bad key, rate limit, etc.)
# it falls through to LLM_2, then LLM_3.
# Recommended: keep LLM_1 and LLM_2 as free-tier providers, LLM_3 as paid backup.
#
# Set in GitHub Actions:
#   Secrets (sensitive):  LLM_1_API_KEY, LLM_2_API_KEY, LLM_3_API_KEY
#   Variables (visible):  LLM_1_PROVIDER, LLM_1_MODEL, LLM_2_PROVIDER, ...
#
# Provider choices: gemini | anthropic | groq | deepseek | openai
# ─────────────────────────────────────────────────────────────────────────────
LLM_CHAIN = [
    {
        "slot": 1,
        "provider": _env("LLM_1_PROVIDER", "gemini"),
        "model":    _env("LLM_1_MODEL",    "gemini-2.0-flash"),
        "api_key":  _env("LLM_1_API_KEY"),
    },
    {
        "slot": 2,
        "provider": _env("LLM_2_PROVIDER", "groq"),
        "model":    _env("LLM_2_MODEL",    "llama-3.3-70b-versatile"),
        "api_key":  _env("LLM_2_API_KEY"),
    },
    {
        "slot": 3,
        "provider": _env("LLM_3_PROVIDER"),
        "model":    _env("LLM_3_MODEL"),
        "api_key":  _env("LLM_3_API_KEY"),
    },
]

RSS_FEEDS = [
    # AI/ML primary sources
    {"url": "https://www.anthropic.com/news.rss", "category": "ai_blog", "name": "Anthropic"},
    {"url": "https://openai.com/news/rss.xml", "category": "ai_blog", "name": "OpenAI"},
    {"url": "https://huggingface.co/blog/feed.xml", "category": "ai_blog", "name": "HuggingFace"},
    {"url": "https://deepmind.google/blog/rss/", "category": "ai_blog", "name": "Google DeepMind"},
    # Tech news
    {"url": "https://techcrunch.com/feed/", "category": "tech_news", "name": "TechCrunch"},
    {"url": "https://www.theverge.com/rss/index.xml", "category": "tech_news", "name": "The Verge"},
    {"url": "https://feeds.arstechnica.com/arstechnica/index", "category": "tech_news", "name": "Ars Technica"},
    {"url": "https://www.wired.com/feed/rss", "category": "tech_news", "name": "Wired"},
    # arXiv
    {"url": "http://arxiv.org/rss/cs.AI", "category": "arxiv", "name": "arXiv CS.AI"},
    {"url": "http://arxiv.org/rss/cs.LG", "category": "arxiv", "name": "arXiv CS.LG"},
]

SOURCE_WEIGHTS = {
    "ai_blog": 20,
    "arxiv": 18,
    "hackernews": 15,
    "tech_news": 12,
}

POSTS_DIR = "content/posts"
COVERED_FILE = "agent/covered.json"

# Unsplash image search (free API key at unsplash.com/developers)
# If not set, posts are generated without images.
UNSPLASH_ACCESS_KEY = _env("UNSPLASH_ACCESS_KEY")
