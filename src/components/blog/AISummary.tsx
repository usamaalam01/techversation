interface AISummaryProps {
  summary: string;
}

export default function AISummary({ summary }: AISummaryProps) {
  return (
    <div className="mb-8 p-5 rounded-2xl bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">✦</span>
        <span className="text-sm font-semibold text-blue-800 dark:text-blue-200 uppercase tracking-wide">
          AI Summary
        </span>
      </div>
      <p className="text-sm text-blue-900 dark:text-blue-100 leading-relaxed">
        {summary}
      </p>
    </div>
  );
}
