// These types describe the JSON that the FastAPI backend sends and receives.
// Each one mirrors a Pydantic class in backend/app/models/schemas.py.
// If you change a schema in the backend, change the matching type here.

// Mirrors DocumentResponse. (Named "UploadedDocument" because "Document" is
// already a built-in browser type, the web page itself. Reusing that name
// would be confusing.)
export interface UploadedDocument {
  document_id: string;
  name: string;
  pages: number;
  chunks: number;
  // JSON has no date type, so the backend's datetime arrives as an ISO string
  // such as "2026-10-07T18:13:13+00:00". We convert it only when displaying.
  uploaded_at: string;
}

// Mirrors SourceResponse: one retrieved chunk that backs up an answer.
export interface Source {
  document_id: string;
  document_name: string;
  page_number: number;
  chunk_index: number;
  similarity: number; // cosine similarity, higher = more similar
  text: string;
}

// Mirrors ChatRequest.
export interface ChatRequest {
  question: string;
  document_id?: string; // optional: leave out to search all documents
}

// Mirrors ChatResponse.
export interface ChatResponse {
  answer: string;
  sources: Source[];
}

// Mirrors GET /health (health.py).
export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
  gemini_configured: boolean;
}