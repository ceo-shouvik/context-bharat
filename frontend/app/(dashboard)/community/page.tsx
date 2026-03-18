/**
 * Community Q&A — questions, answers, and discussion around Indian APIs.
 */
"use client";

import { useEffect, useState } from "react";
import { features } from "@/lib/features";
import { getLibraries, type Library } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.contextbharat.com";

interface Answer {
  id: string;
  author: string;
  body: string;
  created_at: string;
  upvotes: number;
}

interface Question {
  id: string;
  title: string;
  body: string;
  library_id: string;
  library_name?: string;
  tags: string[];
  answers_count: number;
  author: string;
  created_at: string;
  answers?: Answer[];
}

function ComingSoon() {
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">&#128172;</div>
        <h2 className="text-white text-xl font-semibold mb-2">
          Community Q&A — Coming Soon
        </h2>
        <p className="text-gray-400 text-sm max-w-md">
          Ask questions, share knowledge, and help fellow developers integrating
          Indian APIs. Launching soon.
        </p>
      </div>
    </div>
  );
}

function TimeAgo({ date }: { date: string }) {
  const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000);
  if (seconds < 60) return <span>{seconds}s ago</span>;
  if (seconds < 3600) return <span>{Math.floor(seconds / 60)}m ago</span>;
  if (seconds < 86400) return <span>{Math.floor(seconds / 3600)}h ago</span>;
  return <span>{Math.floor(seconds / 86400)}d ago</span>;
}

export default function CommunityPage() {
  const [libraries, setLibraries] = useState<Library[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [filterLibrary, setFilterLibrary] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Ask form state
  const [showAskForm, setShowAskForm] = useState(false);
  const [askTitle, setAskTitle] = useState("");
  const [askBody, setAskBody] = useState("");
  const [askLibrary, setAskLibrary] = useState("");
  const [askTags, setAskTags] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function loadLibraries() {
      try {
        const libs = await getLibraries();
        setLibraries(libs);
      } catch {
        // Non-critical
      }
    }
    loadLibraries();
  }, []);

  useEffect(() => {
    if (!features.communityQa) return;

    async function fetchQuestions() {
      setLoading(true);
      setError(null);
      try {
        const qs = new URLSearchParams();
        if (filterLibrary) qs.set("library_id", filterLibrary);
        const res = await fetch(`${API_BASE}/v1/community/questions?${qs}`);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const data = await res.json();
        setQuestions(data.questions ?? data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load questions");
      } finally {
        setLoading(false);
      }
    }

    fetchQuestions();
  }, [filterLibrary]);

  async function fetchQuestionDetail(q: Question) {
    try {
      const res = await fetch(`${API_BASE}/v1/community/questions/${q.id}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setSelectedQuestion(data);
    } catch {
      setSelectedQuestion(q);
    }
  }

  async function handleAsk() {
    if (!askTitle.trim() || !askBody.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/v1/community/questions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: askTitle,
          body: askBody,
          library_id: askLibrary || undefined,
          tags: askTags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
        }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const newQ = await res.json();
      setQuestions((prev) => [newQ, ...prev]);
      setShowAskForm(false);
      setAskTitle("");
      setAskBody("");
      setAskLibrary("");
      setAskTags("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit question");
    } finally {
      setSubmitting(false);
    }
  }

  if (!features.communityQa) {
    return (
      <div className="min-h-screen bg-[#05080f]"><title>Community — contextBharat</title>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <ComingSoon />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#05080f]"><title>Community — contextBharat</title>
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex items-start justify-between mb-8 flex-wrap gap-4">
          <div>
            <h1 className="text-white text-2xl font-semibold">Community Q&A</h1>
            <p className="text-gray-400 text-sm mt-1">
              Ask questions and share knowledge about Indian API integrations
            </p>
          </div>
          <button
            onClick={() => setShowAskForm(!showAskForm)}
            className="bg-[#f59e1c] text-black text-sm font-medium rounded-lg px-4 py-2 hover:bg-[#f59e1c]/90 transition-colors"
          >
            Ask a Question
          </button>
        </div>

        {/* Ask Form */}
        {showAskForm && (
          <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5 mb-6">
            <h3 className="text-white font-medium mb-4">Ask a Question</h3>
            <div className="grid gap-3">
              <input
                type="text"
                placeholder="Question title"
                value={askTitle}
                onChange={(e) => setAskTitle(e.target.value)}
                className="bg-[#05080f] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
              />
              <textarea
                placeholder="Describe your question in detail..."
                value={askBody}
                onChange={(e) => setAskBody(e.target.value)}
                rows={4}
                className="bg-[#05080f] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none resize-none"
              />
              <div className="grid gap-3 sm:grid-cols-2">
                <select
                  value={askLibrary}
                  onChange={(e) => setAskLibrary(e.target.value)}
                  className="bg-[#05080f] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
                >
                  <option value="">Select library (optional)</option>
                  {libraries.map((lib) => (
                    <option key={lib.library_id} value={lib.library_id}>
                      {lib.name}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="Tags (comma-separated)"
                  value={askTags}
                  onChange={(e) => setAskTags(e.target.value)}
                  className="bg-[#05080f] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 focus:border-[#f59e1c] focus:outline-none"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setShowAskForm(false)}
                  className="text-gray-400 text-sm px-4 py-2 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAsk}
                  disabled={!askTitle.trim() || !askBody.trim() || submitting}
                  className="bg-[#f59e1c] text-black text-sm font-medium rounded-lg px-4 py-2 hover:bg-[#f59e1c]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? "Posting..." : "Post Question"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Filter */}
        <div className="mb-6 max-w-xs">
          <select
            value={filterLibrary}
            onChange={(e) => {
              setFilterLibrary(e.target.value);
              setSelectedQuestion(null);
            }}
            className="bg-[#0c1120] border border-[#1e2d44] text-white text-sm rounded-lg px-3 py-2 w-full focus:border-[#f59e1c] focus:outline-none"
          >
            <option value="">All libraries</option>
            {libraries.map((lib) => (
              <option key={lib.library_id} value={lib.library_id}>
                {lib.name}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400 text-sm mb-6">
            {error}
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-gray-400 text-sm">Loading questions...</div>
          </div>
        )}

        {/* Two-column layout */}
        {!loading && (
          <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
            {/* Questions list */}
            <div className="space-y-3 max-h-[70vh] overflow-y-auto pr-1">
              {questions.length === 0 && (
                <div className="text-center py-12 text-gray-500 text-sm">
                  No questions yet. Be the first to ask!
                </div>
              )}
              {questions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => fetchQuestionDetail(q)}
                  className={`w-full text-left bg-[#0c1120] border rounded-xl p-4 transition-all hover:border-[#f59e1c]/50 ${
                    selectedQuestion?.id === q.id
                      ? "border-[#f59e1c]/60"
                      : "border-[#1e2d44]"
                  }`}
                >
                  <h4 className="text-white text-sm font-medium mb-1.5 line-clamp-2">
                    {q.title}
                  </h4>
                  <div className="flex items-center gap-2 flex-wrap mb-2">
                    {q.library_name && (
                      <span className="text-[10px] bg-[#f59e1c]/10 text-[#f59e1c] border border-[#f59e1c]/20 rounded px-1.5 py-0.5">
                        {q.library_name}
                      </span>
                    )}
                    {q.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded px-1.5 py-0.5"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-3 text-gray-500 text-xs">
                    <span>{q.answers_count} answers</span>
                    <span>{q.author}</span>
                    <TimeAgo date={q.created_at} />
                  </div>
                </button>
              ))}
            </div>

            {/* Detail view */}
            <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5 max-h-[70vh] overflow-y-auto">
              {!selectedQuestion ? (
                <div className="flex items-center justify-center h-full min-h-[300px] text-gray-500 text-sm">
                  Select a question to view details
                </div>
              ) : (
                <div>
                  <h2 className="text-white font-semibold mb-2">{selectedQuestion.title}</h2>
                  <div className="flex items-center gap-2 flex-wrap mb-4">
                    {selectedQuestion.library_name && (
                      <span className="text-xs bg-[#f59e1c]/10 text-[#f59e1c] border border-[#f59e1c]/20 rounded px-2 py-0.5">
                        {selectedQuestion.library_name}
                      </span>
                    )}
                    {selectedQuestion.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded px-2 py-0.5"
                      >
                        {tag}
                      </span>
                    ))}
                    <span className="text-xs text-gray-500">
                      by {selectedQuestion.author} &middot;{" "}
                      <TimeAgo date={selectedQuestion.created_at} />
                    </span>
                  </div>
                  <div className="text-gray-300 text-sm whitespace-pre-wrap mb-6">
                    {selectedQuestion.body}
                  </div>

                  {/* Answers */}
                  {selectedQuestion.answers && selectedQuestion.answers.length > 0 && (
                    <div className="border-t border-[#1e2d44] pt-4">
                      <h3 className="text-white text-sm font-medium mb-3">
                        {selectedQuestion.answers.length} Answer
                        {selectedQuestion.answers.length !== 1 ? "s" : ""}
                      </h3>
                      <div className="space-y-4">
                        {selectedQuestion.answers.map((a) => (
                          <div
                            key={a.id}
                            className="bg-[#05080f] border border-[#1e2d44] rounded-lg p-4"
                          >
                            <div className="text-gray-300 text-sm whitespace-pre-wrap mb-2">
                              {a.body}
                            </div>
                            <div className="flex items-center gap-3 text-gray-500 text-xs">
                              <span>{a.author}</span>
                              <TimeAgo date={a.created_at} />
                              <span>{a.upvotes} upvotes</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedQuestion.answers && selectedQuestion.answers.length === 0 && (
                    <div className="border-t border-[#1e2d44] pt-4 text-gray-500 text-sm">
                      No answers yet. Be the first to answer!
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
