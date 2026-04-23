import { getAllPosts } from "@/lib/posts";
import { generateRSS } from "@/lib/rss";

export const dynamic = "force-static";

export function GET() {
  const posts = getAllPosts();
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://localhost:3000";
  const siteName = process.env.NEXT_PUBLIC_SITE_NAME ?? "AI Pulse";

  const xml = generateRSS(posts, siteUrl, siteName);

  return new Response(xml, {
    headers: {
      "Content-Type": "application/rss+xml; charset=utf-8",
      "Cache-Control": "s-maxage=3600, stale-while-revalidate",
    },
  });
}
