import Image from "next/image";
import { format } from "date-fns";
import Badge from "@/components/ui/Badge";
import type { Post } from "@/types/post";

interface PostHeaderProps {
  post: Post;
}

export default function PostHeader({ post }: PostHeaderProps) {
  return (
    <header className="mb-8">
      <div className="flex flex-wrap gap-2 mb-4">
        {post.tags?.map((tag) => (
          <Badge key={tag} tag={tag} linked />
        ))}
      </div>
      <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-gray-100 leading-tight mb-4">
        {post.title}
      </h1>
      <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
        {post.description}
      </p>
      <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-500 mb-6 pb-6 border-b border-gray-200 dark:border-gray-800">
        <span className="font-medium text-gray-700 dark:text-gray-300">{post.author}</span>
        <span>·</span>
        <span>{format(new Date(post.date), "MMMM d, yyyy")}</span>
        <span>·</span>
        <span>{post.readingTime} min read</span>
      </div>
      {post.coverImage && (
        <div className="relative h-64 md:h-96 rounded-2xl overflow-hidden mb-8">
          <Image
            src={post.coverImage}
            alt={post.title}
            fill
            className="object-cover"
            priority
          />
        </div>
      )}
    </header>
  );
}
