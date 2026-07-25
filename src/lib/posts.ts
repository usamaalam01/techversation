import fs from "fs";
import path from "path";
import matter from "gray-matter";
import readingTime from "reading-time";
import type { Post, SearchIndexItem } from "@/types/post";

const POSTS_DIR = path.join(process.cwd(), "content", "posts");

function getPostFiles(): Array<{ slug: string; filePath: string }> {
  if (!fs.existsSync(POSTS_DIR)) return [];

  const entries = fs.readdirSync(POSTS_DIR, { withFileTypes: true });
  const result: Array<{ slug: string; filePath: string }> = [];

  for (const entry of entries) {
    if (entry.isFile() && entry.name.endsWith(".mdx")) {
      // Flat file: content/posts/slug.mdx (manually created)
      result.push({
        slug: entry.name.replace(/\.mdx$/, ""),
        filePath: path.join(POSTS_DIR, entry.name),
      });
    } else if (entry.isDirectory()) {
      // Directory: content/posts/slug/index.mdx (Keystatic format)
      const indexPath = path.join(POSTS_DIR, entry.name, "index.mdx");
      if (fs.existsSync(indexPath)) {
        result.push({ slug: entry.name, filePath: indexPath });
      }
    }
  }

  return result;
}

function parsePost(slug: string, filePath: string, includeDraft = false): Post | null {
  const raw = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(raw);
  if (data.draft && !includeDraft) return null;

  const rt = readingTime(content);
  return {
    ...(data as Post),
    slug,
    readingTime: Math.ceil(rt.minutes),
    content,
  };
}

// getAllPosts is called from generateStaticParams, generateMetadata, and every
// page render (getRelatedPosts calls it too), so without a cache a build
// re-reads and re-parses the whole content directory thousands of times. Posts
// are read-only for the lifetime of a build, so memoize per process.
// Skipped in development so edits under content/ show up without a restart.
let allPostsCache: Post[] | null = null;

export function getAllPosts(): Post[] {
  if (allPostsCache && process.env.NODE_ENV === "production") {
    return allPostsCache;
  }

  allPostsCache = getPostFiles()
    .map(({ slug, filePath }) => parsePost(slug, filePath))
    .filter((p): p is Post => p !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  return allPostsCache;
}

export function getPostBySlug(slug: string, { includeDraft = false } = {}): Post | null {
  const flat = path.join(POSTS_DIR, `${slug}.mdx`);
  const dir = path.join(POSTS_DIR, slug, "index.mdx");
  const filePath = fs.existsSync(flat) ? flat : fs.existsSync(dir) ? dir : null;
  if (!filePath) return null;
  return parsePost(slug, filePath, includeDraft);
}

export function getPostsByCategory(category: string, limit?: number): Post[] {
  const posts = getAllPosts().filter((p) => p.category === category);
  return limit ? posts.slice(0, limit) : posts;
}

export function getAllTags(): string[] {
  const tagSet = new Set<string>();
  getAllPosts().forEach((post) => post.tags?.forEach((tag) => tagSet.add(tag)));
  return Array.from(tagSet).sort();
}

export function getRelatedPosts(current: Post, limit = 3): Post[] {
  return getAllPosts()
    .filter((p) => p.slug !== current.slug)
    .map((p) => {
      const sharedTags = (p.tags ?? []).filter((t) => current.tags?.includes(t)).length;
      const sameCategory = p.category && p.category === current.category ? 1 : 0;
      return { post: p, score: sharedTags * 2 + sameCategory };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ post }) => post);
}

export function buildSearchIndex(): SearchIndexItem[] {
  return getAllPosts().map(({ slug, title, description, tags, date }) => ({
    slug,
    title,
    description,
    tags,
    date,
  }));
}
