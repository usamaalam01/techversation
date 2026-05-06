import Link from "next/link";
import Image from "next/image";
import { format } from "date-fns";
import Badge from "@/components/ui/Badge";
import type { Post, PostCategory } from "@/types/post";

interface PostCardProps {
  post: Post;
}

const CATEGORY_GRADIENTS: Record<PostCategory, string> = {
  news:      "from-blue-500 to-cyan-400",
  articles:  "from-violet-500 to-purple-400",
  tools:     "from-emerald-500 to-teal-400",
  trending:  "from-orange-500 to-amber-400",
  tutorials: "from-rose-500 to-pink-400",
};

const DEFAULT_GRADIENT = "from-gray-500 to-slate-400";

export default function PostCard({ post }: PostCardProps) {
  const gradient = post.category
    ? (CATEGORY_GRADIENTS[post.category] ?? DEFAULT_GRADIENT)
    : DEFAULT_GRADIENT;

  return (
    <article className="group flex flex-col rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 overflow-hidden hover:shadow-lg transition-shadow">
      <Link href={`/blog/${post.slug}`} className="block overflow-hidden h-48 relative">
        {post.coverImage ? (
          <Image
            src={post.coverImage}
            alt={post.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${gradient} flex items-end p-4`}>
            <span className="text-white/90 text-sm font-medium line-clamp-2 leading-snug">
              {post.title}
            </span>
          </div>
        )}
      </Link>
      <div className="flex flex-col flex-1 p-5 gap-3">
        <div className="flex flex-wrap gap-1.5">
          {post.tags?.map((tag) => (
            <Badge key={tag} tag={tag} linked />
          ))}
        </div>
        <Link href={`/blog/${post.slug}`}>
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
            {post.title}
          </h2>
        </Link>
        <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 flex-1">
          {post.description}
        </p>
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-500 pt-2 border-t border-gray-100 dark:border-gray-800">
          <span>{post.author}</span>
          <div className="flex items-center gap-3">
            <span>{format(new Date(post.date), "MMM d, yyyy")}</span>
            <span>{post.readingTime} min read</span>
          </div>
        </div>
      </div>
    </article>
  );
}
