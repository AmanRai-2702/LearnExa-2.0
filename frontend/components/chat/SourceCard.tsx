"use client";

import { useState } from "react";
import type { Source } from "@/lib/types";

interface SourceCardProps {
  source: Source;
}

export default function SourceCard({ source }: SourceCardProps) {
  // Each card remembers for itself whether its text is expanded.
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-zinc-200 p-3 text-sm dark:border-zinc-800">
      <div className="flex items-center justify-between gap-2">
        <p className="truncate font-medium" title={source.document_name}>
          {source.document_name}
        </p>
        <span className="shrink-0 rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
          Page {source.page_number}
        </span>
      </div>

      <p className="mt-0.5 text-xs text-zinc-500">
        Similarity {source.similarity.toFixed(2)}
      </p>

      {/* line-clamp-3 cuts the text after 3 lines until expanded */}
      <p
        className={`mt-2 whitespace-pre-wrap text-zinc-600 dark:text-zinc-400 ${
          expanded ? "" : "line-clamp-3"
        }`}
      >
        {source.text}
      </p>

      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        aria-expanded={expanded}
        className="mt-2 text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400"
      >
        {expanded ? "Show less" : "Show more"}
      </button>
    </div>
  );
}