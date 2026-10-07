"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, checkHealth, getDocuments } from "@/lib/api";
import type { UploadedDocument } from "@/lib/types";

// The backend check is in exactly one of these situations.
type BackendStatus =
  | { kind: "checking" }
  | { kind: "online"; geminiConfigured: boolean }
  | { kind: "offline" };

const BUTTON = "rounded-lg px-5 py-2.5 text-sm font-medium transition-colors";
const BUTTON_PRIMARY = "bg-indigo-600 text-white hover:bg-indigo-500";
const BUTTON_SECONDARY =
  "border border-zinc-300 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900";
const CARD = "rounded-xl border border-zinc-200 p-5 dark:border-zinc-800";

// A small pill: coloured dot + text.
function StatusPill({ status }: { status: BackendStatus }) {
  let dot = "bg-zinc-400";
  let label = "Checking backend...";

  if (status.kind === "online") {
    dot = status.geminiConfigured ? "bg-green-500" : "bg-amber-500";
    label = status.geminiConfigured
      ? "Backend online"
      : "Backend online, but the Gemini key is missing";
  } else if (status.kind === "offline") {
    dot = "bg-red-500";
    label = "Backend offline";
  }

  return (
    <span
      role="status"
      className="inline-flex items-center gap-2 rounded-full border border-zinc-200 px-3 py-1 text-xs text-zinc-600 dark:border-zinc-800 dark:text-zinc-400"
    >
      <span className={`h-2 w-2 rounded-full ${dot}`} aria-hidden="true" />
      {label}
    </span>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: number | null; // null = still loading
}) {
  return (
    <div className={CARD}>
      <p className="text-sm text-zinc-500">{label}</p>
      <p className="mt-1 text-3xl font-semibold tracking-tight">
        {value === null ? "–" : value.toLocaleString()}
      </p>
    </div>
  );
}

export default function Dashboard() {
  // null means "not loaded yet", so we can tell it apart from "loaded, but empty".
  const [documents, setDocuments] = useState<UploadedDocument[] | null>(null);
  const [documentsError, setDocumentsError] = useState<string | null>(null);
  const [backend, setBackend] = useState<BackendStatus>({ kind: "checking" });

  // Both requests start at the same time and finish independently.
  useEffect(() => {
    checkHealth()
      .then((health) =>
        setBackend({ kind: "online", geminiConfigured: health.gemini_configured })
      )
      .catch(() => setBackend({ kind: "offline" }));

    getDocuments()
      .then((docs) => setDocuments(docs))
      .catch((error: unknown) =>
        setDocumentsError(
          error instanceof ApiError
            ? error.message
            : "Could not load your documents."
        )
      );
  }, []);

  // Derived values: calculated from state on every render, NOT stored in state.
  // (Storing them would create a second copy that could go out of sync.)
  const totalPages = documents?.reduce((sum, doc) => sum + doc.pages, 0) ?? null;
  const totalChunks = documents?.reduce((sum, doc) => sum + doc.chunks, 0) ?? null;
  // The backend already returns newest first, so the first three are the latest.
  const recent = documents?.slice(0, 3) ?? [];

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      {/* Hero */}
      <section className="mb-10">
        <StatusPill status={backend} />
        <h1 className="mt-4 text-4xl font-semibold tracking-tight">
          Learn from your own documents
        </h1>
        <p className="mt-3 max-w-2xl text-zinc-600 dark:text-zinc-400">
          Upload your study material, then ask questions in plain language.
          LearnExa finds the relevant passages and answers from them, showing
          you exactly where each answer came from.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/documents" className={`${BUTTON} ${BUTTON_PRIMARY}`}>
            Upload a document
          </Link>
          <Link href="/chat" className={`${BUTTON} ${BUTTON_SECONDARY}`}>
            Open chat
          </Link>
        </div>
      </section>

      {/* Statistics */}
      <section className="mb-10 grid gap-4 sm:grid-cols-3">
        <StatCard label="Documents" value={documents ? documents.length : null} />
        <StatCard label="Pages" value={totalPages} />
        <StatCard label="Searchable chunks" value={totalChunks} />
      </section>

      {/* Recent documents */}
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-medium">Recent documents</h2>
          {documents && documents.length > 0 && (
            <Link
              href="/documents"
              className="text-sm text-indigo-600 hover:underline dark:text-indigo-400"
            >
              View all
            </Link>
          )}
        </div>

        {documentsError && (
          <p
            role="alert"
            className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
          >
            {documentsError}
          </p>
        )}

        {!documentsError && documents === null && (
          <div className="h-24 animate-pulse rounded-xl bg-zinc-100 dark:bg-zinc-900" />
        )}

        {documents && documents.length === 0 && (
          <div className="rounded-xl border border-dashed border-zinc-300 p-8 text-center dark:border-zinc-700">
            <p className="font-medium">No documents yet</p>
            <p className="mt-1 text-sm text-zinc-500">
              Upload a PDF or TXT file to get started.
            </p>
          </div>
        )}

        {recent.length > 0 && (
          <ul className="divide-y divide-zinc-200 rounded-xl border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
            {recent.map((doc) => (
              <li key={doc.document_id}>
                <Link
                  href={`/chat?document=${encodeURIComponent(doc.document_id)}`}
                  className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-900"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium">📄 {doc.name}</p>
                    <p className="text-sm text-zinc-500">
                      {doc.pages} {doc.pages === 1 ? "page" : "pages"} ·{" "}
                      {doc.chunks} {doc.chunks === 1 ? "chunk" : "chunks"}
                    </p>
                  </div>
                  <span className="shrink-0 text-sm text-indigo-600 dark:text-indigo-400">
                    Chat →
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}