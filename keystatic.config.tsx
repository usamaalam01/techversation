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
      path: "content/posts/*/",
      format: { contentField: "content" },
      schema: {
        title: fields.slug({ name: { label: "Title" } }),
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
        draft: fields.checkbox({ label: "Draft", defaultValue: false }),
        content: fields.mdx({
          label: "Content",
          extension: "mdx",
        }),
      },
    }),
  },
});
