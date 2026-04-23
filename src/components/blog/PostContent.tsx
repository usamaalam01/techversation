import { serializeMDX } from "@/lib/mdx";

interface PostContentProps {
  content: string;
}

export default async function PostContent({ content }: PostContentProps) {
  const { content: mdxContent } = await serializeMDX(content);

  return (
    <div className="prose prose-gray dark:prose-invert max-w-none prose-headings:font-bold prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-code:before:content-none prose-code:after:content-none prose-pre:p-0 prose-pre:bg-transparent">
      {mdxContent}
    </div>
  );
}
