import Link from "next/link";
import NewsletterForm from "@/components/newsletter/NewsletterForm";

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-950 mt-20">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 gap-10 mb-10">
          <div>
            <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-2">AI Pulse</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xs">
              Latest articles on artificial intelligence, LLMs, and tech — some written by humans, some by AI agents.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Stay in the loop</h4>
            <NewsletterForm />
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-4 pt-6 border-t border-gray-200 dark:border-gray-800">
          <div className="flex gap-5">
            <Link href="/blog" className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">Blog</Link>
            <Link href="/search" className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">Search</Link>
            <a href="/rss.xml" className="text-sm text-gray-500 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">RSS</a>
          </div>
          <p className="text-xs text-gray-400">© {new Date().getFullYear()} AI Pulse</p>
        </div>
      </div>
    </footer>
  );
}
