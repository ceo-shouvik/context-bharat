/**
 * CodeBlock — reusable code block with syntax highlighting theme,
 * copy-to-clipboard button, and language label.
 * Used site-wide for all code snippets.
 */
"use client";

import { useState, useCallback } from "react";

interface CodeBlockProps {
  code: string;
  language?: string;
  /** Optional filename or label shown in the header */
  label?: string;
  /** Whether to show the header bar (default true) */
  showHeader?: boolean;
  /** Additional className for the outer wrapper */
  className?: string;
}

export function CodeBlock({
  code,
  language,
  label,
  showHeader = true,
  className = "",
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = code;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [code]);

  return (
    <div
      className={`group relative bg-[#0a0e1a] border border-[#1e2d44] rounded-xl overflow-hidden ${className}`}
    >
      {showHeader && (
        <div className="flex items-center justify-between px-4 py-2.5 border-b border-[#1e2d44] bg-[#0c1120]">
          <div className="flex items-center gap-2">
            {language && (
              <span className="text-[10px] font-mono font-medium uppercase tracking-wider text-gray-500 bg-white/5 px-2 py-0.5 rounded">
                {language}
              </span>
            )}
            {label && (
              <span className="text-xs text-gray-500">{label}</span>
            )}
          </div>
          <CopyButton copied={copied} onClick={handleCopy} />
        </div>
      )}
      <div className="relative">
        {!showHeader && (
          <div className="absolute top-2.5 right-2.5 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
            <CopyButton copied={copied} onClick={handleCopy} />
          </div>
        )}
        <pre className="p-4 overflow-x-auto text-sm leading-relaxed">
          <code className="font-mono text-gray-300">{code}</code>
        </pre>
      </div>
    </div>
  );
}

function CopyButton({ copied, onClick }: { copied: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
        copied
          ? "bg-green-500/15 text-green-400 border border-green-500/30"
          : "bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10 hover:text-white"
      }`}
      aria-label={copied ? "Copied" : "Copy to clipboard"}
    >
      {copied ? (
        <>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          Copied!
        </>
      ) : (
        <>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          Copy
        </>
      )}
    </button>
  );
}
