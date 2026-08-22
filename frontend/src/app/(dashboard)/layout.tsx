"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Brain, LayoutDashboard, Route,
  TrendingUp, User, LogOut, ChevronRight, Cpu
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { Spinner } from "@/components/ui/Spinner";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/roadmap",   icon: Route,           label: "My Roadmap" },
  { href: "/progress",  icon: TrendingUp,      label: "Knowledge Map" },
  { href: "/telemetry", icon: Cpu,             label: "LLM Router" },
  { href: "/profile",   icon: User,            label: "Profile" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, user, logout } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 flex">
      {/* ── Sidebar ──────────────────────────────────────────── */}
      <aside className="w-64 shrink-0 bg-white border-r border-zinc-200 flex flex-col py-6 px-4 min-h-screen sticky top-0 h-screen shadow-card">
        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2.5 px-2 mb-8" style={{ textDecoration: "none" }}>
          <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center shadow-glow-sm">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-base text-black">AdaptRoute</span>
        </Link>

        {/* Nav */}
        <nav className="flex-1 space-y-0.5">
          {navItems.map(({ href, icon: Icon, label }) => {
            const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                style={{ textDecoration: "none" }}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group
                  ${active
                    ? "bg-primary-50 text-primary-700 border border-primary-200"
                    : "text-zinc-600 hover:text-black hover:bg-zinc-100 border border-transparent"
                  }`}
              >
                <Icon className={`w-4 h-4 ${active ? "text-primary-600" : "text-zinc-400 group-hover:text-black"}`} />
                {label}
                {active && <ChevronRight className="w-3 h-3 ml-auto text-primary-500" />}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="border-t border-zinc-200 pt-4 space-y-2">
          {user && (
            <div className="px-3 py-2.5 rounded-xl bg-zinc-50 border border-zinc-200">
              <p className="text-xs text-zinc-400 font-medium uppercase tracking-wide">Signed in as</p>
              <p className="text-sm font-semibold text-black truncate mt-0.5">{user.username}</p>
              <p className="text-xs text-zinc-500 truncate">{user.email}</p>
            </div>
          )}
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-zinc-500 hover:text-red-700 hover:bg-red-50 border border-transparent hover:border-red-200 transition-all duration-200 group"
          >
            <LogOut className="w-4 h-4 group-hover:text-red-600" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── Main Content ─────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto bg-zinc-50">
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="max-w-5xl mx-auto p-8"
        >
          {children}
        </motion.div>
      </main>
    </div>
  );
}
