import type {
  ChatRequest,
  ChatResponse,
  HealthResponse,
  UploadedDocument,
} from "./types";

// Re-exported so existing code (app/page.tsx) that imports HealthResponse
// from "@/lib/api" keeps working.
export type { HealthResponse } from "./types";

// The address of our FastAPI backend.
// If NEXT_PUBLIC_API_URL is set, use it. Otherwise use the local default.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// Every failed API call throws an ApiError. Components only need one
// try/catch and can show error.message directly: it is already human-readable.
export class ApiError extends Error {
  status: number; // HTTP status code, or 0 if the backend could not be reached

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// Pull a readable message out of an error response.
// Our own backend errors look like {"detail": "some text"}.
// FastAPI's automatic validation errors (HTTP 422) put a LIST in "detail",
// so we handle both shapes.
async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      return "That request was not valid. Please check your input and try again.";
    }
  } catch {
    // The body was not JSON (for example a plain 500 page). Use the fallback.
  }
  return `Something went wrong (error ${response.status}). Please try again.`;
}

// The one place that actually calls fetch(). Every function below uses it, so
// "backend unreachable" and "error response" are handled once, not five times.
async function request(path: string, init?: RequestInit): Promise<Response> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    // fetch() only throws when no response arrives at all (backend is off,
    // network problem). An HTTP error like 404 does NOT throw here.
    throw new ApiError("Cannot reach the backend. Is it running on port 8000?", 0);
  }

  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }
  return response;
}

// GET /health
export async function checkHealth(): Promise<HealthResponse> {
  const response = await request("/health");
  return (await response.json()) as HealthResponse;
}

// POST /api/documents/upload
export async function uploadDocument(file: File): Promise<UploadedDocument> {
  // Files travel as multipart form data. The field name "file" must match the
  // parameter name in the backend: upload_document(file: UploadFile).
  const formData = new FormData();
  formData.append("file", file);

  // Do NOT set a Content-Type header here: the browser adds it, including the
  // boundary string that separates the parts of the form.
  const response = await request("/api/documents/upload", {
    method: "POST",
    body: formData,
  });
  return (await response.json()) as UploadedDocument;
}

// GET /api/documents
export async function getDocuments(): Promise<UploadedDocument[]> {
  const response = await request("/api/documents");
  return (await response.json()) as UploadedDocument[];
}

// DELETE /api/documents/{id}
export async function deleteDocument(documentId: string): Promise<void> {
  // The backend answers 204 No Content, so there is no JSON body to read.
  await request(`/api/documents/${encodeURIComponent(documentId)}`, {
    method: "DELETE",
  });
}

// POST /api/chat
export async function sendChatMessage(
  question: string,
  documentId?: string
): Promise<ChatResponse> {
  const body: ChatRequest = { question, document_id: documentId };

  const response = await request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // JSON.stringify drops fields that are undefined, so when documentId is
    // missing, "document_id" is simply not sent.
    body: JSON.stringify(body),
  });
  return (await response.json()) as ChatResponse;
}