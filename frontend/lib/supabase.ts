/**
 * Supabase client instances.
 * Server-side: use createServerClient (with cookies)
 * Client-side: use createBrowserClient (singleton)
 */
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

/** Browser-side Supabase client — singleton */
export const supabase = createClientComponentClient();

/** Type-safe database types — generate with: npx supabase gen types typescript */
export type Database = {
  public: {
    Tables: {
      libraries: {
        Row: {
          id: string;
          library_id: string;
          name: string;
          description: string | null;
          category: string;
          tags: string[] | null;
          freshness_score: number | null;
          last_indexed_at: string | null;
          chunk_count: number;
          is_active: boolean;
        };
      };
      api_keys: {
        Row: {
          id: string;
          user_id: string;
          key_prefix: string;
          name: string | null;
          tier: string;
          daily_limit: number;
          is_active: boolean;
          last_used_at: string | null;
          created_at: string;
        };
      };
    };
  };
};
