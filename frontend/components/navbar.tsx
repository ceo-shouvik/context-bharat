/**
 * Navbar — unified navigation component used across all pages.
 * Consistent links: Libraries, Docs, Pricing, Tools, CTA: Get API Key
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const NAV_LINKS = [
  { href: "/libraries", label: "Libraries" },
  { href: "/docs", label: "Docs" },
  { href: "/pricing", label: "Pricing" },
  { href: "/setup", label: "Tools" },
];

export function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="border-b border-white/10 px-6 py-4">
      <div className="flex items-center justify-between max-w-6xl mx-auto">
        {/* Logo */}
        <Link href="/" className="font-bold text-[#f59e1c] text-xl flex-shrink-0">
          context<span className="text-white">Bharat</span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-6 text-sm">
          {NAV_LINKS.map(({ href, label }) => {
            const isActive = pathname === href || pathname.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={`transition-colors ${
                  isActive ? "text-white font-medium" : "text-gray-400 hover:text-white"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </div>

        {/* CTA + mobile toggle */}
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="bg-[#f59e1c] text-black px-4 py-2 rounded-lg text-sm font-semibold hover:bg-[#fbbf45] transition-colors"
          >
            Get API Key
          </Link>
          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden text-gray-400 hover:text-white transition-colors p-1"
            aria-label="Toggle menu"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              {mobileOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </>
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden mt-4 pb-2 border-t border-white/10 pt-4">
          <div className="flex flex-col gap-3">
            {NAV_LINKS.map(({ href, label }) => {
              const isActive = pathname === href || pathname.startsWith(href + "/");
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={() => setMobileOpen(false)}
                  className={`text-sm px-2 py-1.5 rounded transition-colors ${
                    isActive ? "text-white font-medium bg-white/5" : "text-gray-400 hover:text-white"
                  }`}
                >
                  {label}
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </nav>
  );
}
