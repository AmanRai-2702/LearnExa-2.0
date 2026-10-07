import type { UploadedDocument } from "@/lib/types";
import DocumentCard from "./DocumentCard";

interface DocumentListProps {
  documents: UploadedDocument[];
  onDelete: (document: UploadedDocument) => void;
  deletingId: string | null; // which document is being deleted right now, if any
}

export default function DocumentList({
  documents,
  onDelete,
  deletingId,
}: DocumentListProps) {
  // Empty state: nothing uploaded yet.
  if (documents.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-zinc-300 p-10 text-center dark:border-zinc-700">
        <p className="font-medium">No documents yet</p>
        <p className="mt-1 text-sm text-zinc-500">
          Upload a PDF or TXT file to start asking questions about it.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {documents.map((document) => (
        <DocumentCard
          key={document.document_id}
          document={document}
          onDelete={onDelete}
          isDeleting={deletingId === document.document_id}
        />
      ))}
    </div>
  );
}