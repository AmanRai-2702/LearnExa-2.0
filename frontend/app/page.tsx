"use client";

import { useEffect, useState } from "react";
import { checkHealth, type HealthResponse } from "@/lib/api";

export default function Home() {
  // State: values the page remembers. When they change, the page redraws.
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // useEffect with [] runs once, right after the page first appears.
  useEffect(() => {
    checkHealth()
      .then((data) => setHealth(data))
      .catch(() =>
        setError("Cannot reach the backend. Is it running on port 8000?")
      );
  }, []);

  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-8">
      <h1 className="text-4xl font-semibold tracking-tight">LearnExa</h1>
      <p className="text-zinc-600 dark:text-zinc-400">
        Upload your study material and ask questions about it.
      </p>

      <div className="rounded-xl border border-zinc-200 p-5 dark:border-zinc-800">
        <h2 className="mb-2 text-sm font-medium uppercase text-zinc-500">
          Backend status
        </h2>

        {error && <p className="text-red-500">{error}</p>}

        {!error && !health && <p>Checking...</p>}

        {health && (
          <ul className="space-y-1">
            <li>Status: {health.status}</li>
            <li>App: {health.app}</li>
            <li>Environment: {health.environment}</li>
            <li>
              Gemini key configured: {health.gemini_configured ? "yes" : "no"}
            </li>
          </ul>
        )}
      </div>
    </main>
  );
}