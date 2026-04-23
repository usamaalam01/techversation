"use client";

import { useState, useEffect, useRef } from "react";
import Fuse from "fuse.js";
import Link from "next/link";
import type { SearchIndexItem } from "@/types/post";

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchIndexItem[]>([]);
  const [index, setIndex] = useState<SearchIndexItem[]>([]);
  const fuseRef = useRef<Fuse<SearchIndexItem> | null>(null);

  useEffect(() => {
    fetch("/search-index.json")
      .then((r) => r.json())
      .then((data: SearchIndexItem[]) => {
        setIndex(data);
        fuseRef.current = new Fuse(data, {
          keys: ["title", "description", "tags"],
          threshold: 0.35,
        });
      });
  }, []);

  useEffect(() => {
    if (!query.trim() || !fuseRef.current) {
      setResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setResults(fuseRef.current!.search(query).map((r) => r.item));
    }, 300);
    return () => clearTimeout(timer);
  }, [query, index]);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search articles…"
        autoFocus
        className="w-full px-5 py-3 text-lg rounded-2xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {query && (
        <div className="mt-6">
          {results.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No results for &ldquo;{query}&rdquo;
            </p>
          ) : (
            <ul className="flex flex-col gap-3">
              {results.map((item) => (
                <li key={item.slug}>
                  <Link
                    href={`/blog/${item.slug}`}
                    className="block p-4 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:border-blue-400 transition-colors"
                  >
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">{item.title}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-1">
                      {item.description}
                    </p>
                    <div className="flex gap-1.5 mt-2">
                      {item.tags?.map((t) => (
                        <span
                          key={t}
                          className="text-xs px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
