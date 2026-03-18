/**
 * Dashboard layout — wraps protected pages with auth check.
 * Redirects to /login if no active Supabase session.
 */
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { AuthChangeEvent, Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    checkSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event: AuthChangeEvent, session: Session | null) => {
      if (!session) {
        router.push("/login");
      } else {
        setAuthenticated(true);
      }
    });

    return () => subscription.unsubscribe();
  }, [router]);

  async function checkSession() {
    const {
      data: { session },
    } = await supabase.auth.getSession();
    if (!session) {
      router.push("/login");
    } else {
      setAuthenticated(true);
    }
    setLoading(false);
  }

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-[#05080f] flex items-center justify-center">
        <div className="text-gray-400 text-sm">Loading...</div>
      </div>
    );
  }

  if (!authenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[#05080f]">
      {/* Dashboard Nav */}
      <nav className="border-b border-white/10 px-6 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="font-bold text-[#f59e1c] text-lg">
              context<span className="text-white">Bharat</span>
            </Link>
            <div className="flex gap-4 text-sm">
              <Link
                href="/dashboard"
                className="text-gray-400 hover:text-white transition-colors"
              >
                Dashboard
              </Link>
              <Link
                href="/libraries"
                className="text-gray-400 hover:text-white transition-colors"
              >
                Libraries
              </Link>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-gray-400 text-sm hover:text-white transition-colors"
          >
            Sign out
          </button>
        </div>
      </nav>
      {children}
    </div>
  );
}
