import Link from "next/link";
import type { UploadedDocument } from "@/lib/types";

// Props: the inputs this component receives from its parent.
interface DocumentCardProps {
  document: UploadedDocument;
  onDelete: (document: UploadedDocument) => void;
  isDeleting: boolean;
}

const CARD =
  "flex flex-col gap-4 rounded-xl border border-zinc-200 p-5 dark:border-zinc-800";
const BUTTON = "rounded-md px-3 py-1.5 text-sm font-medium transition-colors";
const BUTTON_OPEN =
  "bg-indigo-600 text-white hover:bg-indigo-500";
const BUTTON_DELETE =
  "text-red-600 hover:bg-red-50 disabled:opacity-50 dark:text-red-400 dark:hover:bg-red-950";

// "1 page", "2 pages"
function plural(count: number, word: string): string {
  return `${count} ${word}${count === 1 ? "" : "s"}`;
}

// Turn an ISO date string into "3 hours ago", "yesterday", etc.
function timeAgo(isoDate: string): string {
  const seconds = Math.round((new Date(isoDate).getTime() - Date.now()) / 1000);
  const formatter = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  const units: [Intl.RelativeTimeFormatUnit, number][] = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
  ];
  for (const [unit, size] of units) {
    if (Math.abs(seconds) >= size) {
      return formatter.format(Math.round(seconds / size), unit);
    }
  }
  return "just now";
}

export default function DocumentCard({
  document,
  onDelete,
  isDeleting,
}: DocumentCardProps) {
  return (
    <div className={CARD}>
      <div className="flex items-start gap-3">
        <span className="text-2xl" aria-hidden="true">
          📄
        </span>
        <div className="min-w-0">
          {/* truncate = cut long names with "..." instead of breaking the layout */}
          <h3 className="truncate font-medium" title={document.name}>
            {document.name}
          </h3>
          <p className="text-sm text-zinc-500">
            {plural(document.pages, "page")} · {plural(document.chunks, "chunk")}
          </p>
        </div>
      </div>

      <p className="text-sm text-zinc-500">
        Uploaded {timeAgo(document.uploaded_at)}
      </p>

      <div className="flex items-center justify-between">
        {/* The chat page (built later) will read ?document=<id> */}
        <Link
          href={`/chat?document=${encodeURIComponent(document.document_id)}`}
          className={`${BUTTON} ${BUTTON_OPEN}`}
        >
          Open
        </Link>
        <button
          type="button"
          onClick={() => onDelete(document)}
          disabled={isDeleting}
          className={`${BUTTON} ${BUTTON_DELETE}`}
        >
          {isDeleting ? "Deleting..." : "Delete"}
        </button>
      </div>
    </div>
  );
}