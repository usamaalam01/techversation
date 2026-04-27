import re
from pathlib import Path


def inject_cover_image(mdx: str, url: str) -> str:
    """Add or replace the coverImage field in MDX frontmatter."""
    if re.search(r"^coverImage:", mdx, re.MULTILINE):
        return re.sub(r'^coverImage:.*$', f'coverImage: "{url}"', mdx, flags=re.MULTILINE)
    # Insert before the draft: line
    return re.sub(r'^(draft:)', f'coverImage: "{url}"\n\\1', mdx, flags=re.MULTILINE)


def _slugify(title: str) -> str:
    title = title.strip("\"'")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:80]


def _extract_title(mdx: str) -> str:
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', mdx, re.MULTILINE)
    return match.group(1).strip() if match else "untitled-post"


def validate_mdx(mdx: str, min_words: int = 400) -> bool:
    """Return True if the generated MDX meets minimum quality requirements."""
    if mdx.count("---") < 2:
        print("[Writer] Validation failed: missing frontmatter delimiters")
        return False

    for field in ("title:", "description:", "date:", "author:", "tags:", "draft:"):
        if field not in mdx:
            print(f"[Writer] Validation failed: missing frontmatter field '{field}'")
            return False

    parts = mdx.split("---", 2)
    if len(parts) < 3:
        print("[Writer] Validation failed: malformed frontmatter block")
        return False

    word_count = len(parts[2].split())
    if word_count < min_words:
        print(f"[Writer] Validation failed: body too short ({word_count} words, min {min_words})")
        return False

    return True


def write_post(mdx: str, posts_dir: str) -> str:
    """Write the MDX file to content/posts/{slug}.mdx. Returns the slug used."""
    base_slug = _slugify(_extract_title(mdx))
    posts_path = Path(posts_dir)
    posts_path.mkdir(parents=True, exist_ok=True)

    slug = base_slug
    counter = 2
    while (posts_path / f"{slug}.mdx").exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    file_path = posts_path / f"{slug}.mdx"
    file_path.write_text(mdx, encoding="utf-8")
    print(f"[Writer] Saved: {file_path}")
    return slug
