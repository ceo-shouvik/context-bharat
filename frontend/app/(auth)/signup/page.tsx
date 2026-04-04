/**
 * Signup page — redirects to login since we use OAuth (no separate signup flow).
 * This prevents 404s when links or users navigate to /signup.
 */
import { redirect } from "next/navigation";

export default function SignupPage() {
  redirect("/login");
}
