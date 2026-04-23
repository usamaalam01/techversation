import fs from "fs";
import path from "path";
import matter from "gray-matter";
import readingTime from "reading-time";
import type { Post, SearchIndexItem } from "@/types/post";

const POSTS_DIR = path.join(process.cwd(), "content", "posts");

function slugFromFilename(filename: string): string {
  return filename.replace(/\.mdx?$/, "");
}

export function getAllPosts(): Post[] {
  if (!fs.existsSync(POSTS_DIR)) return [];

  const filenames = fs.readdirSync(POSTS_DIR).filter((f) => f.endsWith(".mdx"));

  const posts = filenames
    .map((filename) => {
      const slug = slugFromFilename(filename);
      const raw = fs.readFileSync(path.join(POSTS_DIR, filename), "utf-8");
      const { data, content } = matter(raw);
      const rt = readingTime(content);

      return {
        ...(data as Post),
        slug,
        readingTime: Math.ceil(rt.minutes),
        content,
      } as Post;
    })
    .filter((post) => !post.draft);

  return posts.sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );
}

export function getPostBySlug(slug: string): Post | null {
  const filePath = path.join(POSTS_DIR, `${slug}.mdx`);
  if (!fs.existsSync(filePath)) return null;

  const raw = fs.readFileSync(filePath, "utf-8");
  const { data, content } = matter(raw);
  const rt = readingTime(content);

  return {
    ...(data as Post),
    slug,
    readingTime: Math.ceil(rt.minutes),
    content,
  } as Post;
}

export function getAllTags(): string[] {
  const posts = getAllPosts();
  const tagSet = new Set<string>();
  posts.forEach((post) => post.tags?.forEach((tag) => tagSet.add(tag)));
  return Array.from(tagSet).sort();
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
