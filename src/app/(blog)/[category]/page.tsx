import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getPostsByCategory } from "@/lib/posts";
import { POST_CATEGORIES } from "@/types/post";
import PostCard from "@/components/blog/PostCard";

interface CategoryPageProps {
  params: Promise<{ category: string }>;
}

export function generateStaticParams() {
  return POST_CATEGORIES.map((c) => ({ category: c.id }));
}

export async function generateMetadata({ params }: CategoryPageProps): Promise<Metadata> {
  const { category } = await params;
  const cat = POST_CATEGORIES.find((c) => c.id === category);
  if (!cat) return {};
  return {
    title: cat.label,
    description: cat.description,
  };
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const { category } = await params;
  const cat = POST_CATEGORIES.find((c) => c.id === category);
  if (!cat) notFound();

  const posts = getPostsByCategory(category);

  return (
    <main className="max-w-5xl mx-auto px-4 py-12">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">{cat.label}</h1>
        <p className="text-gray-600 dark:text-gray-400">{cat.description}</p>
      </div>

      {posts.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400 text-center py-20">
          No posts in this category yet — check back soon.
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
