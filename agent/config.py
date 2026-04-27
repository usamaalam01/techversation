import os

MAX_AGE_HOURS = int(os.environ.get("MAX_AGE_HOURS", "48"))
HN_MIN_SCORE = int(os.environ.get("HN_MIN_SCORE", "100"))
POSTS_PER_RUN = int(os.environ.get("POSTS_PER_RUN", "1"))

# LLM provider config — all switchable via environment variables.
# Provider choices: gemini | anthropic | groq | deepseek | openai
# Set these in GitHub Actions repo variables/secrets (or .env for local runs).
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")
LLM_MODEL = os.environ.get("LLM_MODEL", "gemini-2.0-flash")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")

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
