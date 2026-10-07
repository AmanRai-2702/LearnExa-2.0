import type { Message } from "@/lib/types";
import SourceCard from "./SourceCard";

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  // Each early return handles one kind of message. After the check,
  // TypeScript knows exactly which fields that kind has.
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap break-words rounded-2xl rounded-br-sm bg-indigo-600 px-4 py-2.5 text-white">
          {message.text}
        </div>
      </div>
    );
  }

  if (message.role === "error") {
    return (
      <div
        role="alert"
        className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
      >
        {message.text}
      </div>
    );
  }

  // The only remaining kind is "assistant".
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
        LearnExa
      </p>
      <div className="whitespace-pre-wrap break-words leading-relaxed">
        {message.text}
      </div>

      {/* No sources (for example "no documents uploaded") means no Sources section. */}
      {message.sources.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-zinc-500">
            Sources
          </p>
          <div className="grid gap-2 sm:grid-cols-2">
            {message.sources.map((source) => (
              <SourceCard
                key={`${source.document_id}-${source.chunk_index}`}
                source={source}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}