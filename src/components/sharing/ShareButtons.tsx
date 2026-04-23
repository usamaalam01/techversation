"use client";

import { useState } from "react";

interface ShareButtonsProps {
  title: string;
  slug: string;
}

export default function ShareButtons({ title, slug }: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "";
  const url = `${siteUrl}/blog/${slug}`;
  const encoded = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);

  function copyLink() {
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  const btnClass =
    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 transition-colors";

  return (
    <div className="flex flex-wrap items-center gap-2 mt-10 pt-6 border-t border-gray-200 dark:border-gray-800">
      <span className="text-sm text-gray-500 dark:text-gray-400 mr-1">Share:</span>
      <a
        href={`https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encoded}`}
        target="_blank"
        rel="noopener noreferrer"
        className={btnClass}
      >
        𝕏 Twitter
      </a>
      <a
        href={`https://www.linkedin.com/sharing/share-offsite/?url=${encoded}`}
        target="_blank"
        rel="noopener noreferrer"
        className={btnClass}
      >
        LinkedIn
      </a>
      <a
        href={`https://reddit.com/submit?url=${encoded}&title=${encodedTitle}`}
        target="_blank"
        rel="noopener noreferrer"
        className={btnClass}
      >
        Reddit
      </a>
      <button onClick={copyLink} className={btnClass}>
        {copied ? "✓ Copied!" : "Copy Link"}
      </button>
    </div>
  );
}
