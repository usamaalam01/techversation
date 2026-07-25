import { notFound } from "next/navigation";
import { draftMode } from "next/headers";
import type { Metadata } from "next";
import { getAllPosts, getPostBySlug, getRelatedPosts } from "@/lib/posts";
import PostHeader from "@/components/blog/PostHeader";
import PostContent from "@/components/blog/PostContent";
import AISummary from "@/components/blog/AISummary";
import RelatedPosts from "@/components/blog/RelatedPosts";
import ShareButtons from "@/components/sharing/ShareButtons";
import GiscusComments from "@/components/comments/GiscusComments";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "";

interface PostPageProps {
  params: Promise<{ slug: string }>;
}

// Vercel caps the build step at 45 minutes. Prerendering every post pushed us
// past that once the archive grew, so only the newest posts are built ahead of
// time; the rest render on first request (dynamicParams defaults to true) and
// are cached from then on.
const PRERENDERED_POSTS = 200;

export async function generateStaticParams() {
  return getAllPosts()
    .slice(0, PRERENDERED_POSTS)
    .map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: PostPageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) return {};

  const ogImage = post.coverImage ?? "/og-default.png";

  return {
    title: post.title,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      publishedTime: post.date,
      authors: [post.author],
      images: [{ url: `${SITE_URL}${ogImage}` }],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.description,
      images: [`${SITE_URL}${ogImage}`],
    },
  };
}

export default async function PostPage({ params }: PostPageProps) {
  const { slug } = await params;
  const { isEnabled: preview } = await draftMode();

  const post = getPostBySlug(slug, { includeDraft: preview });
  if (!post) notFound();

  const related = getRelatedPosts(post);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.description,
    datePublished: post.date,
    author: { "@type": "Person", name: post.author },
    image: `${SITE_URL}${post.coverImage ?? "/og-default.png"}`,
    url: `${SITE_URL}/blog/${post.slug}`,
  };

  return (
    <>
      {preview && (
        <div className="sticky top-14 z-40 bg-amber-400 text-amber-950 text-sm font-medium px-4 py-2 flex items-center justify-between">
          <span>Draft preview — this post is not yet published</span>
          <a href="/api/disable-preview" className="underline hover:no-underline">
            Exit preview
          </a>
        </div>
      )}
      <article className="max-w-3xl mx-auto px-4 py-12">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <PostHeader post={post} />
        {post.aiSummary && <AISummary summary={post.aiSummary} />}
        <PostContent content={post.content} />
        <RelatedPosts posts={related} />
        <ShareButtons title={post.title} slug={post.slug} />
        <GiscusComments slug={post.slug} />
      </article>
    </>
  );
}
