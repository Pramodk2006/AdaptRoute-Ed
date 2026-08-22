/**
 * /profile/setup redirects to /profile — same page, different entry URL
 * used after registration for clarity in the URL.
 */
import { redirect } from "next/navigation";

export default function ProfileSetupPage() {
  redirect("/profile");
}
