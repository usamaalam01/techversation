import type { Metadata } from "next";
import SearchBar from "@/components/search/SearchBar";

export const metadata: Metadata = {
  title: "Search",
  description: "Search all articles on AI Pulse.",
};

export default function SearchPage() {
  return (
    <main className="max-w-5xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">Search articles</h1>
      <SearchBar />
    </main>
  );
}
