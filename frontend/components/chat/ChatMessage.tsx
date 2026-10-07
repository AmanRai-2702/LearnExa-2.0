import ReactMarkdown, { type Components } from "react-markdown";
import type { Message } from "@/lib/types";
import SourceCard from "./SourceCard";

interface ChatMessageProps {
  message: Message;
}

// Custom rendering for specific markdown elements. Here: links open in a NEW
// tab, so clicking one never navigates away from the conversation.
// rel="noopener noreferrer" stops the opened page from getting access to ours.
// (Defined outside the component so it is created only once.)
const MARKDOWN_COMPONENTS: Components = {
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
};

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

      {/* ReactMarkdown turns "**bold**" and "- item" into real HTML elements.
          The "markdown" class (globals.css) styles them. */}
      <div className="markdown break-words leading-relaxed">
        <ReactMarkdown components={MARKDOWN_COMPONENTS}>
          {message.text}
        </ReactMarkdown>
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