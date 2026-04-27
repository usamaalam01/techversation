export type PostCategory = "news" | "articles" | "tools" | "trending" | "tutorials";

export const POST_CATEGORIES: { id: PostCategory; label: string; description: string }[] = [
  { id: "news",      label: "News",      description: "Latest breaking news in AI and tech." },
  { id: "articles",  label: "Articles",  description: "Deep dives and opinion pieces from top AI labs." },
  { id: "tools",     label: "Tools",     description: "New tools, APIs, and frameworks worth trying." },
  { id: "trending",  label: "Trending",  description: "What the tech community is buzzing about." },
  { id: "tutorials", label: "Tutorials", description: "Step-by-step guides and technical how-tos." },
];

export interface PostFrontmatter {
  title: string;
  description: string;
  date: string;
  author: string;
  tags: string[];
  coverImage?: string;
  aiSummary?: string;
  category?: PostCategory;
  draft: boolean;
}

export interface Post extends PostFrontmatter {
  slug: string;
  readingTime: number;
  content: string;
}

export interface SearchIndexItem {
  slug: string;
  title: string;
  description: string;
  tags: string[];
  date: string;
}
