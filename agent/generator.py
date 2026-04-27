"""
LLM content generation via LangChain.
Switch provider/model/key entirely through env vars — no code changes needed.

Supported providers (LLM_PROVIDER env var):
  gemini     → Google Gemini (default, free tier available)
  anthropic  → Anthropic Claude
  groq       → Groq (free tier, Llama models)
  deepseek   → DeepSeek (OpenAI-compatible API)
  openai     → OpenAI GPT models

Example env vars:
  LLM_PROVIDER=gemini      LLM_MODEL=gemini-2.0-flash          LLM_API_KEY=AIza...
  LLM_PROVIDER=anthropic   LLM_MODEL=claude-sonnet-4-6         LLM_API_KEY=sk-ant-...
  LLM_PROVIDER=groq        LLM_MODEL=llama-3.3-70b-versatile   LLM_API_KEY=gsk_...
  LLM_PROVIDER=deepseek    LLM_MODEL=deepseek-chat             LLM_API_KEY=sk-...
  LLM_PROVIDER=openai      LLM_MODEL=gpt-4o-mini               LLM_API_KEY=sk-...
"""
import time
from datetime import date
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config

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


def _build_llm():
    """Instantiate the correct LangChain chat model based on LLM_PROVIDER."""
    provider = config.LLM_PROVIDER.lower()
    model = config.LLM_MODEL
    api_key = config.LLM_API_KEY

    if not api_key:
        raise RuntimeError(
            f"LLM_API_KEY is not set. "
            f"Add it as a GitHub Actions secret or export it locally."
        )

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.7,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            temperature=0.7,
            max_tokens=4096,
        )

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            groq_api_key=api_key,
            temperature=0.7,
        )

    if provider == "deepseek":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1",
            temperature=0.7,
            max_tokens=4096,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            temperature=0.7,
            max_tokens=4096,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. "
        f"Choose from: gemini, anthropic, groq, deepseek, openai"
    )


def generate_post(story: dict[str, Any], retries: int = 3) -> str:
    """Generate a full MDX blog post for the given story. Returns raw MDX string."""
    llm = _build_llm()
    fmt = story["_format"]
    today = date.today().isoformat()

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Write {_FORMAT_DESCRIPTIONS[fmt]} about the following story.\n\n"
            f"Story title: {story['title']}\n"
            f"Source: {story['source_name']}\n"
            f"URL: {story['url']}\n"
            f"Description: {story.get('description') or 'No description available.'}\n"
            f"Post date: {today}\n"
            f"Target length: {_FORMAT_LENGTHS[fmt]}\n"
        )),
    ]

    print(f"[Generator] Using {config.LLM_PROVIDER}/{config.LLM_MODEL}")

    for attempt in range(retries):
        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            if attempt < retries - 1:
                wait = 5 * (2 ** attempt)  # 5s, 10s, 20s
                print(f"[Generator] Error: {e} — retrying in {wait}s (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                raise RuntimeError(
                    f"LLM ({config.LLM_PROVIDER}/{config.LLM_MODEL}) failed "
                    f"after {retries} attempts: {e}"
                ) from e
