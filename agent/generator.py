"""
LLM content generation with a 3-slot fallback chain via LangChain.

The agent tries LLM_1 first. On any failure (quota exhausted, invalid key,
rate limit, provider outage) it falls through to LLM_2, then LLM_3.
Keep LLM_1/LLM_2 as free-tier providers and LLM_3 as a paid safety net.

Supported providers (LLM_N_PROVIDER env var):
  gemini     → Google Gemini  (free tier: 1 500 req/day)
  groq       → Groq           (free tier: generous daily limits)
  anthropic  → Anthropic Claude
  deepseek   → DeepSeek       (OpenAI-compatible API)
  openai     → OpenAI

Example config (GitHub Actions Variables + Secrets):
  LLM_1_PROVIDER=gemini    LLM_1_MODEL=gemini-2.0-flash          LLM_1_API_KEY=AIza...
  LLM_2_PROVIDER=groq      LLM_2_MODEL=llama-3.3-70b-versatile   LLM_2_API_KEY=gsk_...
  LLM_3_PROVIDER=anthropic LLM_3_MODEL=claude-haiku-4-5-20251001 LLM_3_API_KEY=sk-ant-...
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

_CATEGORY_GUIDANCE = {
    "news": (
        "This post belongs to the News category. "
        "Write a concise, timely news analysis — what happened, why it matters, what comes next. "
        "Keep it punchy and to the point."
    ),
    "articles": (
        "This post belongs to the Articles category. "
        "Write an in-depth, opinionated piece. Explore implications, trade-offs, and developer impact. "
        "Back opinions with reasoning."
    ),
    "tools": (
        "This post belongs to the Tools category. "
        "Write a practical tutorial or hands-on review of the new tool/API/framework. "
        "Show real code examples, explain how to get started, and give an honest assessment."
    ),
    "trending": (
        "This post belongs to the Trending category. "
        "Write a sharp analysis of why this topic is blowing up right now. "
        "Capture the community sentiment and give your honest take."
    ),
    "tutorials": (
        "This post belongs to the Tutorials category. "
        "Write a clear, step-by-step guide. Start from scratch, build to something useful. "
        "Prioritize working code, clear explanations, and practical takeaways."
    ),
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
- Do not add any text before the opening ---
- If inline image URLs are provided in the user message, use 1–2 of them naturally \
in the body using standard markdown: ![descriptive alt text](url). \
Only place images where they genuinely add value — after explaining a concept, \
to break up a long section, or to illustrate a point. Never place images inside code blocks.\
"""


def _build_llm(provider: str, model: str, api_key: str):
    """Instantiate the LangChain chat model for the given provider."""
    provider = provider.lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model, google_api_key=api_key, temperature=0.7,
        )
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model, anthropic_api_key=api_key, temperature=0.7, max_tokens=4096,
        )
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model, groq_api_key=api_key, temperature=0.7,
        )
    if provider == "deepseek":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model, openai_api_key=api_key,
            openai_api_base="https://api.deepseek.com/v1", temperature=0.7, max_tokens=4096,
        )
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model, openai_api_key=api_key, temperature=0.7, max_tokens=4096,
        )

    raise ValueError(
        f"Unknown provider '{provider}'. "
        f"Choose from: gemini, anthropic, groq, deepseek, openai"
    )


def _invoke_llm(llm_cfg: dict[str, Any], messages: list) -> str:
    """
    Try a single LLM slot once (plus one quick retry for transient network errors).
    Raises on failure so the caller can fall through to the next slot.
    """
    provider = llm_cfg["provider"]
    model = llm_cfg["model"]
    slot = llm_cfg["slot"]
    label = f"LLM {slot} ({provider}/{model})"

    llm = _build_llm(provider, model, llm_cfg["api_key"])

    for attempt in range(2):  # 1 retry per slot for transient blips
        try:
            print(f"[Generator] {label} — attempt {attempt + 1}")
            response = llm.invoke(messages)
            print(f"[Generator] {label} — success")
            return response.content
        except Exception as e:
            if attempt == 0:
                print(f"[Generator] {label} — transient error: {e!r}, retrying in 5s")
                time.sleep(5)
            else:
                raise  # Let outer loop catch and fall through to next slot


def generate_post(story: dict[str, Any], inline_images: list[dict] | None = None, category: str | None = None) -> str:
    """
    Generate a full MDX post using the fallback chain.
    Tries each configured LLM slot in order; falls through on any failure.
    Raises RuntimeError if all slots fail.
    """
    # Only include slots that have both provider and api_key set
    chain = [s for s in config.LLM_CHAIN if s.get("provider") and s.get("api_key")]

    if not chain:
        raise RuntimeError(
            "No LLMs configured. Set at least LLM_1_PROVIDER and LLM_1_API_KEY."
        )

    fmt = story["_format"]
    today = date.today().isoformat()

    image_section = ""
    if inline_images:
        lines = ["Inline images available for use in the post body (use 1–2 where appropriate):"]
        for i, img in enumerate(inline_images, 1):
            lines.append(f"  Image {i}: {img['url']}  (suggested alt: \"{img['alt']}\")")
        image_section = "\n\n" + "\n".join(lines)

    category_section = ""
    if category and category in _CATEGORY_GUIDANCE:
        category_section = f"\n\nCategory context: {_CATEGORY_GUIDANCE[category]}"

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Write {_FORMAT_DESCRIPTIONS[fmt]} about the following story.\n\n"
            f"Story title: {story['title']}\n"
            f"Source: {story['source_name']}\n"
            f"URL: {story['url']}\n"
            f"Description: {story.get('description') or 'No description available.'}\n"
            f"Post date: {today}\n"
            f"Target length: {_FORMAT_LENGTHS[fmt]}"
            f"{category_section}"
            f"{image_section}\n"
        )),
    ]

    errors: list[str] = []

    for llm_cfg in chain:
        slot = llm_cfg["slot"]
        provider = llm_cfg["provider"]
        model = llm_cfg["model"]
        label = f"LLM {slot} ({provider}/{model})"
        try:
            return _invoke_llm(llm_cfg, messages)
        except Exception as e:
            msg = f"{label} failed: {e!r}"
            print(f"[Generator] {msg}")
            errors.append(msg)
            if llm_cfg is not chain[-1]:
                print(f"[Generator] Falling back to next LLM...")

    raise RuntimeError(
        f"All {len(chain)} LLM(s) in the chain failed.\n" + "\n".join(errors)
    )
