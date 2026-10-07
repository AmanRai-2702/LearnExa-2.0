"use client";

import { useEffect, useState } from "react";
import DocumentList from "@/components/documents/DocumentList";
import { ApiError, deleteDocument, getDocuments } from "@/lib/api";
import type { UploadedDocument } from "@/lib/types";

// api.ts always throws ApiError, whose message is already user-friendly.
function errorMessage(error: unknown): string {
  return error instanceof ApiError
    ? error.message
    : "Something went wrong. Please try again.";
}

// Grey pulsing placeholders shown while the list loads.
function LoadingSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((n) => (
        <div
          key={n}
          className="h-36 animate-pulse rounded-xl bg-zinc-100 dark:bg-zinc-900"
        />
      ))}
    </div>
  );
}

export default function DocumentsPage() {
  // State: things this page remembers. Changing any of them redraws the page.
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  // Changing this number re-runs the effect below. It powers the Retry button.
  const [reloadKey, setReloadKey] = useState(0);

  // Runs after the first render, and again whenever reloadKey changes
  // (that is what the [reloadKey] dependency list means).
  useEffect(() => {
    getDocuments()
      .then((docs) => setDocuments(docs))
      .catch((err: unknown) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, [reloadKey]);

  function handleRetry() {
    setError(null);
    setLoading(true);
    setReloadKey((key) => key + 1);
  }

  async function handleDelete(document: UploadedDocument) {
    // window.confirm is the simplest possible "are you sure?" dialog.
    const confirmed = window.confirm(
      `Delete "${document.name}"? Its searchable content will be removed too.`
    );
    if (!confirmed) return;

    setDeletingId(document.document_id);
    setError(null);
    try {
      await deleteDocument(document.document_id);
      // Backend succeeded, so drop the document from our list without refetching.
      setDocuments((current) =>
        current.filter((d) => d.document_id !== document.document_id)
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Documents</h1>
        <p className="mt-1 text-zinc-600 dark:text-zinc-400">
          {loading
            ? "Loading your documents..."
            : `${documents.length} ${documents.length === 1 ? "document" : "documents"} ready to chat with.`}
        </p>
      </header>

      {loading ? (
        <LoadingSkeleton />
      ) : (
        <>
          {error && (
            <div
              role="alert"
              className="mb-6 flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
            >
              <span>{error}</span>
              <button
                type="button"
                onClick={handleRetry}
                className="shrink-0 rounded-md px-3 py-1.5 font-medium hover:bg-red-100 dark:hover:bg-red-900"
              >
                Try again
              </button>
            </div>
          )}

          {/* If loading failed, don't also claim "No documents yet". */}
          {(documents.length > 0 || !error) && (
            <DocumentList
              documents={documents}
              onDelete={handleDelete}
              deletingId={deletingId}
            />
          )}
        </>
      )}
    </main>
  );
}