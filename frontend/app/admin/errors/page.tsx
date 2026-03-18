"use client";

import { useEffect, useState } from "react";
import { adminFetch } from "@/lib/admin-api";

interface IngestionError {
  id: string;
  library_id: string;
  error_message: string;
  stage: string;
  timestamp: string;
  ticket_url?: string;
}

export default function AdminErrors() {
  const [errors, setErrors] = useState<IngestionError[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState("");
  const [creatingTicket, setCreatingTicket] = useState<string | null>(null);

  useEffect(() => {
    loadErrors();
  }, []);

  async function loadErrors() {
    try {
      const data = await adminFetch<{ errors: IngestionError[] }>("/v1/admin/errors");
      setErrors(data.errors);
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : "Failed to load errors");
    } finally {
      setLoading(false);
    }
  }

  async function createTicket(errorId: string) {
    setCreatingTicket(errorId);
    try {
      const result = await adminFetch<{ ticket_url: string }>(
        `/v1/admin/errors/${errorId}/create-ticket`,
        { method: "POST" },
      );
      setErrors((prev) =>
        prev.map((e) => (e.id === errorId ? { ...e, ticket_url: result.ticket_url } : e)),
      );
    } catch {
      // Silently fail
    } finally {
      setCreatingTicket(null);
    }
  }

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading errors...</div>;
  }

  if (fetchError) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
        {fetchError}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Error Log</h1>
        <p className="text-gray-500 text-sm mt-1">
          Ingestion errors and ticket creation
        </p>
      </div>

      {errors.length === 0 ? (
        <div className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-8 text-center text-gray-500 text-sm">
          No errors recorded.
        </div>
      ) : (
        <div className="space-y-3">
          {errors.map((err) => (
            <div
              key={err.id}
              className="bg-[#0c1120] border border-[#1e2d44] rounded-lg p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-white">{err.error_message}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span className="text-[#f59e1c]">{err.library_id}</span>
                    <span>&middot;</span>
                    <span>Stage: {err.stage}</span>
                    <span>&middot;</span>
                    <span>{new Date(err.timestamp).toLocaleString()}</span>
                  </div>
                  {err.ticket_url && (
                    <a
                      href={err.ticket_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block mt-2 text-xs text-blue-400 hover:underline"
                    >
                      View Ticket &rarr;
                    </a>
                  )}
                </div>
                <div className="flex-shrink-0">
                  {err.ticket_url ? (
                    <span className="px-2.5 py-1 rounded text-xs bg-green-500/10 text-green-400">
                      Ticket Created
                    </span>
                  ) : (
                    <button
                      onClick={() => createTicket(err.id)}
                      disabled={creatingTicket === err.id}
                      className={`px-3 py-1.5 rounded text-xs font-medium bg-[#f59e1c]/10 text-[#f59e1c] hover:bg-[#f59e1c]/20 transition-colors ${
                        creatingTicket === err.id ? "opacity-50" : ""
                      }`}
                    >
                      {creatingTicket === err.id ? "Creating..." : "Create Ticket"}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
