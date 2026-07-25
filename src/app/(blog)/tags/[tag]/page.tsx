import type { Metadata } from "next";
import { getAllPosts } from "@/lib/posts";
import PostCard from "@/components/blog/PostCard";

interface TagPageProps {
  params: Promise<{ tag: string }>;
}

// See the note in blog/[slug]/page.tsx: most tags match only a handful of
// posts, so prerender the busiest ones and leave the long tail on demand.
const PRERENDERED_TAGS = 50;

export async function generateStaticParams() {
  const counts = new Map<string, number>();
  for (const post of getAllPosts()) {
    for (const tag of post.tags ?? []) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1);
    }
  }
  return Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, PRERENDERED_TAGS)
    .map(([tag]) => ({ tag }));
}

export async function generateMetadata({ params }: TagPageProps): Promise<Metadata> {
  const { tag } = await params;
  return {
    title: `#${tag}`,
    description: `Articles tagged with ${tag}.`,
  };
}

export default async function TagPage({ params }: TagPageProps) {
  const { tag } = await params;
  const posts = getAllPosts().filter((p) => p.tags?.includes(tag));

  return (
    <main className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
        #{tag}
      </h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">
        {posts.length} article{posts.length !== 1 ? "s" : ""}
      </p>
      {posts.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No articles with this tag.</p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </div>
      )}
    </main>
  );
}
