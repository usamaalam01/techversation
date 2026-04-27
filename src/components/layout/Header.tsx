"use client";

import Link from "next/link";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { POST_CATEGORIES } from "@/types/post";

export default function Header() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => setMounted(true), []);

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-950/80 backdrop-blur border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link
          href="/"
          className="font-bold text-lg text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          Techversation
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {POST_CATEGORIES.map((cat) => (
            <Link
              key={cat.id}
              href={`/${cat.id}`}
              className="px-3 py-1.5 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {cat.label}
            </Link>
          ))}
          <Link
            href="/blog"
            className="px-3 py-1.5 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            All
          </Link>
          <Link
            href="/search"
            className="px-3 py-1.5 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            Search
          </Link>
          {mounted && (
            <button
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
              aria-label="Toggle theme"
              className="ml-1 p-1.5 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {resolvedTheme === "dark" ? "☀️" : "🌙"}
            </button>
          )}
        </nav>

        {/* Mobile nav toggle */}
        <div className="flex md:hidden items-center gap-2">
          {mounted && (
            <button
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
              aria-label="Toggle theme"
              className="p-1.5 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {resolvedTheme === "dark" ? "☀️" : "🌙"}
            </button>
          )}
          <button
            onClick={() => setMenuOpen((o) => !o)}
            aria-label="Toggle menu"
            className="p-1.5 rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {menuOpen ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <nav className="md:hidden border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3 flex flex-col gap-1">
          {POST_CATEGORIES.map((cat) => (
            <Link
              key={cat.id}
              href={`/${cat.id}`}
              onClick={() => setMenuOpen(false)}
              className="px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              {cat.label}
            </Link>
          ))}
          <Link
            href="/blog"
            onClick={() => setMenuOpen(false)}
            className="px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            All posts
          </Link>
          <Link
            href="/search"
            onClick={() => setMenuOpen(false)}
            className="px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            Search
          </Link>
        </nav>
      )}
    </header>
  );
}
