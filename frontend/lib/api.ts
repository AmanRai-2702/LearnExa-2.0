// The address of our FastAPI backend.
// If NEXT_PUBLIC_API_URL is set, use it. Otherwise use the local default.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// The shape of the JSON that GET /health returns.
// This must match what health.py in the backend sends back.
export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
  gemini_configured: boolean;
}

// Ask the backend "are you alive?" and return its answer.
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Backend returned status ${response.status}`);
  }

  return response.json();
}