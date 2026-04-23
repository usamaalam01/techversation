export interface PostFrontmatter {
  title: string;
  description: string;
  date: string;
  author: string;
  tags: string[];
  coverImage?: string;
  aiSummary?: string;
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
