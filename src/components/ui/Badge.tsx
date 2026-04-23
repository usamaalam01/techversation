import Link from "next/link";

interface BadgeProps {
  tag: string;
  linked?: boolean;
}

export default function Badge({ tag, linked = false }: BadgeProps) {
  const classes =
    "inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors";

  if (linked) {
    return (
      <Link href={`/tags/${tag}`} className={classes}>
        {tag}
      </Link>
    );
  }
  return <span className={classes}>{tag}</span>;
}
