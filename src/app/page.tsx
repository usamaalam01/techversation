import Link from "next/link";
import { getAllPosts } from "@/lib/posts";
import PostCard from "@/components/blog/PostCard";
import NewsletterForm from "@/components/newsletter/NewsletterForm";

export default function HomePage() {
  const posts = getAllPosts();
  const featured = posts.slice(0, 3);

  return (
    <main>
      {/* Hero */}
      <section className="max-w-5xl mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-gray-100 mb-4 leading-tight">
          Stay ahead of<br />
          <span className="text-blue-600 dark:text-blue-400">artificial intelligence</span>
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-xl mx-auto mb-8">
          Deep dives into LLMs, AI agents, and emerging tech — published by humans and AI alike.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/blog"
            className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors"
          >
            Read articles
          </Link>
          <Link
            href="/search"
            className="px-6 py-3 rounded-xl border border-gray-300 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 font-medium transition-colors"
          >
            Search
          </Link>
        </div>
      </section>

      {/* Latest posts */}
      {featured.length > 0 && (
        <section className="max-w-5xl mx-auto px-4 pb-16">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Latest articles</h2>
            <Link href="/blog" className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
              View all →
            </Link>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {featured.map((post) => (
              <PostCard key={post.slug} post={post} />
            ))}
          </div>
        </section>
      )}

      {/* Newsletter CTA */}
      <section className="max-w-5xl mx-auto px-4 pb-20">
        <div className="rounded-2xl bg-blue-600 dark:bg-blue-700 p-10 text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Never miss a post</h2>
          <p className="text-blue-100 mb-6 text-sm">Get new articles delivered to your inbox.</p>
          <div className="flex justify-center">
            <NewsletterForm />
          </div>
        </div>
      </section>
    </main>
  );
}
