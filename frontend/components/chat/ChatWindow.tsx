"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/lib/types";
import ChatMessage from "./ChatMessage";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSuggestionClick: (question: string) => void;
}

const SUGGESTIONS = [
  "Summarize the main ideas of this document.",
  "What are the key terms I should know?",
  "Explain the most important concept in simple words.",
];

export default function ChatWindow({
  messages,
  isLoading,
  onSuggestionClick,
}: ChatWindowProps) {
  // A ref is a handle to a real DOM element. This one points at an empty marker
  // at the very bottom of the conversation.
  const bottomRef = useRef<HTMLDivElement>(null);

  // Whenever a message arrives (or the thinking indicator appears/disappears),
  // scroll the marker into view so the newest content is visible.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isLoading]);

  // Empty state: nothing said yet.
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-4 text-center">
        <div>
          <p className="text-lg font-medium">Ask anything about your documents</p>
          <p className="mt-1 text-sm text-zinc-500">
            Answers come from your uploaded material, with the sources shown.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => onSuggestionClick(suggestion)}
              className="rounded-full border border-zinc-300 px-4 py-2 text-sm transition-colors hover:border-indigo-400 hover:bg-indigo-50 dark:border-zinc-700 dark:hover:bg-indigo-950/40"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    // min-h-0 + overflow-y-auto: this area scrolls on its own while the Navbar
    // and the input stay put.
    <div className="flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto py-6">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-zinc-500" role="status">
          <span className="flex gap-1" aria-hidden="true">
            {[0, 150, 300].map((delay) => (
              <span
                key={delay}
                className="h-2 w-2 animate-bounce rounded-full bg-zinc-400"
                style={{ animationDelay: `${delay}ms` }}
              />
            ))}
          </span>
          Searching your documents and thinking...
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}