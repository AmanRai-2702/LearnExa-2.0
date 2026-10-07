"use client";

import { useState } from "react";
import type { KeyboardEvent } from "react";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled: boolean; // true while waiting for an answer
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  // "Controlled input": React state is the single source of truth for what the
  // textarea shows. Every keystroke updates state, and state feeds the textarea.
  const [text, setText] = useState("");

  const canSend = text.trim().length > 0 && !disabled;

  function submit() {
    if (!canSend) return;
    onSend(text.trim());
    setText("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends. Shift+Enter falls through and inserts a new line as normal.
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault(); // stop the newline that Enter would add
      submit();
    }
  }

  return (
    <div className="border-t border-zinc-200 py-4 dark:border-zinc-800">
      <div className="flex items-end gap-2">
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          maxLength={1000} // same limit as the backend (ChatRequest)
          placeholder="Ask about your documents..."
          aria-label="Your question"
          className="field-sizing-content max-h-40 min-h-11 flex-1 resize-none rounded-xl border border-zinc-300 bg-transparent px-4 py-2.5 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 dark:border-zinc-700"
        />
        <button
          type="button"
          onClick={submit}
          disabled={!canSend}
          className="h-11 rounded-xl bg-indigo-600 px-5 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </div>
      <p className="mt-2 text-xs text-zinc-500">
        Enter to send, Shift+Enter for a new line
      </p>
    </div>
  );
}