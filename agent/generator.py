import os
import time
from datetime import date
from typing import Any

import anthropic

_FORMAT_LENGTHS = {
    "analysis": "600–900 words",
    "tutorial": "1200–2000 words, include working code examples",
    "explainer": "800–1200 words, make the concepts accessible to developers",
}

_FORMAT_DESCRIPTIONS = {
    "analysis": (
        "a news analysis post: summarize what happened, explain why it matters "
        "to developers, and give your take on the broader implications"
    ),
    "tutorial": (
        "a practical tutorial or deep-dive: show developers how to use or work "
        "with this new tool/model/API, with concrete code examples"
    ),
    "explainer": (
        "a research paper explainer: make the paper accessible to developers, "
        "cover the key ideas in plain language, and explain the practical implications"
    ),
}

_SYSTEM_PROMPT = """\
You are a technical blog writer for Techversation, an AI/tech blog for software developers and AI practitioners.

Writing style:
- Clear, direct, and developer-first. No hype, no filler.
- Opinionated but fair. Back up opinions with reasoning.
- Show code where it helps understanding.
- Conversational but precise.

Output format — you MUST output a complete MDX blog post with this exact structure:

---
title: "Post title here"
description: "Meta description, 120–160 characters, plain sentence."
date: "YYYY-MM-DD"
author: "Usama"
tags: ["tag1", "tag2", "tag3"]
aiSummary: "2–3 sentence summary shown at the top of the post to give readers a quick overview."
draft: true
---

Post body here...

Rules:
- tags: 3–5 lowercase single-word or hyphenated tags (e.g. "ai", "llm", "python", "open-source")
- title: max 80 characters, compelling but not clickbait
- description: max 160 characters, no questions, no "In this post..."
- aiSummary: standalone sentences, not "This post covers..."
- Use ## for section headings, ### for subsections
- Code blocks must have language hints (```python, ```typescript, ```bash, etc.)
- Link naturally to the original source within the body text
- End the post body with this line on its own paragraph: *This post was drafted with AI assistance.*
- Do not add any text before the opening ---\
"""


def generate_post(story: dict[str, Any], retries: int = 3) -> str:
    """Call Claude to generate a full MDX post. Returns the raw MDX string."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = date.today().isoformat()
    fmt = story["_format"]

    user_prompt = (
        f"Write {_FORMAT_DESCRIPTIONS[fmt]} about the following story.\n\n"
        f"Story title: {story['title']}\n"
        f"Source: {story['source_name']}\n"
        f"URL: {story['url']}\n"
        f"Description: {story.get('description') or 'No description available.'}\n"
        f"Post date: {today}\n"
        f"Target length: {_FORMAT_LENGTHS[fmt]}\n"
    )

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except anthropic.RateLimitError as e:
            wait = 10 * (2 ** attempt)
            print(f"[Generator] Rate limit, waiting {wait}s (attempt {attempt + 1}/{retries})")
            time.sleep(wait)
            last_error = e
        except anthropic.APIError as e:
            wait = 5 * (2 ** attempt)
            print(f"[Generator] API error: {e}, retrying in {wait}s (attempt {attempt + 1}/{retries})")
            time.sleep(wait)
            last_error = e

    raise RuntimeError(f"Claude API failed after {retries} attempts: {last_error}")
