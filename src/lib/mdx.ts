import { compileMDX } from "next-mdx-remote/rsc";
import rehypePrettyCode from "rehype-pretty-code";
import type { Options as PrettyCodeOptions } from "rehype-pretty-code";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

const prettyCodeOptions: PrettyCodeOptions = {
  theme: {
    dark: "github-dark",
    light: "github-light",
  },
  keepBackground: false,
};

export async function serializeMDX(source: string) {
  const result = await compileMDX({
    source,
    options: {
      parseFrontmatter: false,
      mdxOptions: {
        // remarkMath claims `$...$` / `$$...$$` before MDX treats `{` inside
        // LaTeX (e.g. `o_{1:t}`) as a JSX expression and fails to parse it.
        remarkPlugins: [remarkGfm, remarkMath],
        rehypePlugins: [
          rehypeKatex,
          [rehypePrettyCode, prettyCodeOptions],
        ],
      },
    },
  });
  return result;
}
