import { config, collection, fields } from "@keystatic/core";

export default config({
  storage: { kind: "local" },
  ui: {
    brand: { name: "AI Pulse" },
  },
  collections: {
    posts: collection({
      label: "Posts",
      slugField: "title",
      path: "content/posts/*",
      format: { contentField: "content" },
      schema: {
        title: fields.text({ label: "Title", validation: { length: { min: 1 } } }),
        description: fields.text({
          label: "Description",
          multiline: true,
          validation: { length: { min: 1 } },
        }),
        date: fields.date({
          label: "Publish Date",
          defaultValue: { kind: "today" },
        }),
        author: fields.text({ label: "Author", defaultValue: "Usama" }),
        tags: fields.array(fields.text({ label: "Tag" }), {
          label: "Tags",
          itemLabel: (props) => props.value || "Tag",
        }),
        coverImage: fields.image({
          label: "Cover Image",
          directory: "public/images/posts",
          publicPath: "/images/posts/",
        }),
        aiSummary: fields.text({
          label: "AI Summary",
          description: "Short summary shown at the top of the post.",
          multiline: true,
        }),
        category: fields.select({
          label: "Category",
          description: "Section this post belongs to.",
          options: [
            { label: "News",      value: "news" },
            { label: "Articles",  value: "articles" },
            { label: "Tools",     value: "tools" },
            { label: "Trending",  value: "trending" },
            { label: "Tutorials", value: "tutorials" },
          ],
          defaultValue: "articles",
        }),
        draft: fields.checkbox({ label: "Draft", defaultValue: false }),
        content: fields.mdx({
          label: "Content",
          extension: "mdx",
        }),
      },
    }),
  },
});
