import { Suspense } from "react";
import { getAllPosts, getAllTags } from "@/lib/posts";
import PostCard from "@/components/blog/PostCard";
import TagFilter from "@/components/blog/TagFilter";

interface BlogPageProps {
  searchParams: Promise<{ tag?: string }>;
}

export const metadata = {
  title: "Blog",
  description: "All articles on AI, LLMs, and technology.",
};

export default async function BlogPage({ searchParams }: BlogPageProps) {
  const { tag } = await searchParams;
  const allPosts = getAllPosts();
  const tags = getAllTags();

  const posts = tag ? allPosts.filter((p) => p.tags?.includes(tag)) : allPosts;

  return (
    <main className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">All articles</h1>

      <Suspense>
        <div className="mb-8">
          <TagFilter tags={tags} />
        </div>
      </Suspense>

      {posts.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400 text-center py-16">
          No articles found{tag ? ` for tag "${tag}"` : ""}.
        </p>
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
