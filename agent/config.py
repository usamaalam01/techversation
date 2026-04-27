import os

# GitHub Actions doesn't allow empty secret values, so placeholders like "-"
# are used instead. This helper normalises them all to an empty string.
_PLACEHOLDERS = {"-", "none", "null", "n/a", "na", "placeholder", "undefined"}

def _env(key: str, default: str = "") -> str:
    val = os.environ.get(key, default).strip()
    return "" if val.lower() in _PLACEHOLDERS else val


MAX_AGE_HOURS = int(os.environ.get("MAX_AGE_HOURS", "48"))
HN_MIN_SCORE = int(os.environ.get("HN_MIN_SCORE", "100"))
POSTS_PER_RUN = int(os.environ.get("POSTS_PER_RUN", "1"))

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
