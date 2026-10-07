"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import ChatInput from "@/components/chat/ChatInput";
import ChatWindow from "@/components/chat/ChatWindow";
import { ApiError, getDocuments, sendChatMessage } from "@/lib/api";
import type { Message, UploadedDocument } from "@/lib/types";

function ChatPageContent() {
  // Reads "?document=<id>" from the URL (the Open button on a document card).
  const searchParams = useSearchParams();

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  // "" means "search all documents".
  const [selectedId, setSelectedId] = useState(searchParams.get("document") ?? "");

  // Load the documents once, for the dropdown.
  useEffect(() => {
    getDocuments()
      .then((docs) => {
        setDocuments(docs);
        // If the URL pointed at a document that no longer exists, fall back to "all".
        setSelectedId((current) =>
          docs.some((doc) => doc.document_id === current) ? current : ""
        );
      })
      .catch(() => {
        // Not fatal here: the dropdown just offers "All documents". If the
        // backend is really down, sending a question shows a proper error.
      });
  }, []);

  async function handleSend(question: string) {
    if (isLoading) return;

    // State is never changed in place. We build a NEW array: the old messages
    // plus one more. (The function form of the setter always sees the latest list.)
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", text: question },
    ]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(question, selectedId || undefined);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "error",
          text:
            error instanceof ApiError
              ? error.message
              : "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    // 3.5rem is the Navbar height (h-14). The chat fills exactly the rest of the screen.
    <main className="mx-auto flex h-[calc(100dvh-3.5rem)] w-full max-w-3xl flex-col px-4">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-200 py-4 dark:border-zinc-800">
        <h1 className="text-xl font-semibold tracking-tight">Chat</h1>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-zinc-500">
            Search in
            <select
              value={selectedId}
              onChange={(event) => setSelectedId(event.target.value)}
              disabled={isLoading}
              className="max-w-48 rounded-md border border-zinc-300 bg-background px-2 py-1 text-sm text-foreground dark:border-zinc-700"
            >
              <option value="">All documents</option>
              {documents.map((doc) => (
                <option key={doc.document_id} value={doc.document_id}>
                  {doc.name}
                </option>
              ))}
            </select>
          </label>

          {messages.length > 0 && (
            <button
              type="button"
              onClick={() => setMessages([])}
              disabled={isLoading}
              className="text-sm text-zinc-500 hover:text-foreground disabled:opacity-50"
            >
              Clear
            </button>
          )}
        </div>
      </header>

      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        onSuggestionClick={handleSend}
      />

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </main>
  );
}

// useSearchParams needs a Suspense boundary (see the Next.js docs): without it,
// `npm run build` fails. The page itself is just the wrapper.
export default function ChatPage() {
  return (
    <Suspense
      fallback={<main className="flex-1 p-8 text-zinc-500">Loading chat...</main>}
    >
      <ChatPageContent />
    </Suspense>
  );
}