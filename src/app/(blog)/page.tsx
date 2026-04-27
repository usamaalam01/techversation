import Link from "next/link";
import { getPostsByCategory } from "@/lib/posts";
import { POST_CATEGORIES } from "@/types/post";
import PostCard from "@/components/blog/PostCard";
import NewsletterForm from "@/components/newsletter/NewsletterForm";

const CATEGORY_ICONS: Record<string, string> = {
  news:      "📰",
  articles:  "✍️",
  tools:     "🛠️",
  trending:  "🔥",
  tutorials: "📚",
};

export default function HomePage() {
  const categorySections = POST_CATEGORIES.map((cat) => ({
    ...cat,
    posts: getPostsByCategory(cat.id, 3),
  }));

  const hasAnyPost = categorySections.some((s) => s.posts.length > 0);

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
        <div className="flex flex-wrap gap-3 justify-center">
          {POST_CATEGORIES.map((cat) => (
            <Link
              key={cat.id}
              href={`/${cat.id}`}
              className="px-4 py-2 rounded-xl border border-gray-300 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 font-medium transition-colors"
            >
              {CATEGORY_ICONS[cat.id]} {cat.label}
            </Link>
          ))}
        </div>
      </section>

      {/* Category sections */}
      {hasAnyPost ? (
        categorySections.map((section) =>
          section.posts.length > 0 ? (
            <section key={section.id} className="max-w-5xl mx-auto px-4 pb-16">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {CATEGORY_ICONS[section.id]} {section.label}
                </h2>
                <Link
                  href={`/${section.id}`}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  View all →
                </Link>
              </div>
              <div className="grid md:grid-cols-3 gap-6">
                {section.posts.map((post) => (
                  <PostCard key={post.slug} post={post} />
                ))}
              </div>
            </section>
          ) : null
        )
      ) : (
        <section className="max-w-5xl mx-auto px-4 pb-16 text-center py-16">
          <p className="text-gray-500 dark:text-gray-400">
            No posts yet — the AI agent will publish soon. Check back shortly!
          </p>
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
