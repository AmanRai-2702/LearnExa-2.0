"use client";

import { useEffect, useState } from "react";
import type { DragEvent, ChangeEvent } from "react";
import { ApiError, uploadDocument } from "@/lib/api";
import type { UploadedDocument } from "@/lib/types";

// These mirror the rules in the backend (document_service.py).
// The backend ALWAYS re-checks them: browser checks are only for fast feedback.
const ALLOWED_EXTENSIONS = [".pdf", ".txt"];
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024; // 10 MB

// The upload is always in exactly one of these situations. Each one carries only
// the data that makes sense for it (a "discriminated union": check .kind first).
type UploadStatus =
  | { kind: "idle" }
  | { kind: "uploading"; fileName: string }
  | { kind: "success"; document: UploadedDocument }
  | { kind: "error"; message: string };

interface UploadZoneProps {
  // Called after a successful upload so the parent page can show the new document.
  onUploaded: (document: UploadedDocument) => void;
}

const ZONE_BASE =
  "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-10 text-center transition-colors focus-within:ring-2 focus-within:ring-indigo-500";
const ZONE_IDLE =
  "border-zinc-300 hover:border-indigo-400 dark:border-zinc-700 dark:hover:border-indigo-500";
const ZONE_DRAGGING =
  "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/40";
const ZONE_BUSY = "cursor-wait border-zinc-300 opacity-70 dark:border-zinc-700";

// Returns a problem description, or null if the file looks fine.
function validateFile(file: File): string | null {
  const name = file.name.toLowerCase();
  if (!ALLOWED_EXTENSIONS.some((extension) => name.endsWith(extension))) {
    return "Unsupported file type. Please upload a PDF or TXT file.";
  }
  if (file.size === 0) {
    return "This file is empty.";
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    return `This file is too large. The limit is ${MAX_UPLOAD_BYTES / (1024 * 1024)} MB.`;
  }
  return null;
}

export default function UploadZone({ onUploaded }: UploadZoneProps) {
  const [status, setStatus] = useState<UploadStatus>({ kind: "idle" });
  const [isDragging, setIsDragging] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const isUploading = status.kind === "uploading";

  // A stopwatch while uploading. The backend cannot report progress (it answers
  // only when the whole document is processed), so a running timer shows the
  // user that the app has not frozen.
  useEffect(() => {
    if (!isUploading) return;
    const timer = setInterval(() => setElapsedSeconds((s) => s + 1), 1000);
    // The returned function is the "cleanup": React runs it when the upload
    // ends (or the component disappears), so the timer never keeps ticking.
    return () => clearInterval(timer);
  }, [isUploading]);

  async function handleFile(file: File) {
    const problem = validateFile(file);
    if (problem) {
      setStatus({ kind: "error", message: problem });
      return;
    }

    setElapsedSeconds(0);
    setStatus({ kind: "uploading", fileName: file.name });
    try {
      const document = await uploadDocument(file);
      setStatus({ kind: "success", document });
      onUploaded(document);
    } catch (error) {
      setStatus({
        kind: "error",
        message:
          error instanceof ApiError
            ? error.message
            : "Upload failed. Please try again.",
      });
    }
  }

  // Fired when the user picks a file in the browser's file dialog.
  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    // Clear the input so choosing the SAME file again still triggers onChange.
    event.target.value = "";
    if (file) void handleFile(file);
  }

  // Drag and drop: three events matter.
  function handleDragOver(event: DragEvent<HTMLLabelElement>) {
    // Browsers refuse drops unless dragover is cancelled. This line is required.
    event.preventDefault();
    if (!isUploading) setIsDragging(true);
  }

  function handleDragLeave() {
    setIsDragging(false);
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    // Without this the browser would open the dropped file in the tab.
    event.preventDefault();
    setIsDragging(false);
    if (isUploading) return;
    const file = event.dataTransfer.files[0];
    if (file) void handleFile(file);
  }

  const zoneStyle = isUploading ? ZONE_BUSY : isDragging ? ZONE_DRAGGING : ZONE_IDLE;

  return (
    <div className="mb-8">
      {/* A <label> wraps the hidden input, so clicking anywhere on the zone opens
          the file dialog. No extra code needed. */}
      <label
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`${ZONE_BASE} ${zoneStyle}`}
      >
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleInputChange}
          disabled={isUploading}
          className="sr-only"
        />

        {/* pointer-events-none stops the text from triggering dragleave flicker */}
        <div className="pointer-events-none flex flex-col items-center gap-2">
          <span className="text-3xl" aria-hidden="true">
            {isUploading ? "⏳" : "⬆️"}
          </span>
          {isUploading ? (
            <>
              <p className="font-medium">Processing {status.fileName}...</p>
              <p className="text-sm text-zinc-500">
                {elapsedSeconds}s elapsed. Large PDFs can take a few minutes, so
                please keep this page open.
              </p>
            </>
          ) : (
            <>
              <p className="font-medium">
                Drag a file here, or{" "}
                <span className="text-indigo-600 dark:text-indigo-400">browse</span>
              </p>
              <p className="text-sm text-zinc-500">PDF or TXT, up to 10 MB</p>
            </>
          )}
        </div>
      </label>

      {status.kind === "success" && (
        <p
          role="status"
          className="mt-3 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-800 dark:bg-green-950 dark:text-green-300"
        >
          Added “{status.document.name}”: {status.document.pages}{" "}
          {status.document.pages === 1 ? "page" : "pages"},{" "}
          {status.document.chunks}{" "}
          {status.document.chunks === 1 ? "chunk" : "chunks"}. You can chat with it now.
        </p>
      )}

      {status.kind === "error" && (
        <p
          role="alert"
          className="mt-3 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-300"
        >
          {status.message}
        </p>
      )}
    </div>
  );
}