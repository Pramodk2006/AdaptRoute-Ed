"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  TrendingUp, BookOpen, ClipboardCheck, Zap,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { DashboardStats } from "@/lib/types";
import { Spinner } from "@/components/ui/Spinner";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

function StatCard({
  icon: Icon, label, value, sub, accentClass,
}: {
  icon: React.ElementType; label: string; value: string | number;
  sub?: string; accentClass: string;
}) {
  return (
    <Card>
      <CardContent>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-zinc-400 mb-1">{label}</p>
            <p className={`font-display text-3xl font-bold text-black`}>{value}</p>
            {sub && <p className="text-xs text-zinc-500 mt-1">{sub}</p>}
          </div>
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${accentClass}`}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ProgressRing({ pct }: { pct: number }) {
  const r = 54;
  const circ = 2 * Math.PI * r;
  const dash = ((100 - pct) / 100) * circ;
  return (
    <div className="relative flex items-center justify-center w-36 h-36">
      <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={r} fill="none" strokeWidth="10" className="stroke-zinc-100" />
        <circle
          cx="60" cy="60" r={r} fill="none" strokeWidth="10"
          stroke="url(#prog)" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={dash}
          style={{ transition: "stroke-dashoffset 1s ease" }}
        />
        <defs>
          <linearGradient id="prog" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute text-center">
        <span className="font-display text-2xl font-bold text-black">{pct}%</span>
        <p className="text-xs text-zinc-500">done</p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => api.get<DashboardStats>("/dashboard").then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const noRoadmap = !stats?.roadmap_status;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-display text-3xl font-bold text-black">
          Welcome back, <span className="text-primary-600">{user?.username}</span> 👋
        </h1>
        <p className="text-zinc-500 mt-1">
          {noRoadmap
            ? "You don't have a roadmap yet. Let's build one!"
            : `Your learning journey is ${stats?.completion_percentage ?? 0}% complete.`}
        </p>
      </motion.div>

      {/* No roadmap CTA */}
      {noRoadmap && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white border-2 border-black rounded-2xl p-8 flex flex-col sm:flex-row items-center gap-6"
        >
          <div className="flex-1">
            <h2 className="font-display text-xl font-bold text-black mb-2">
              Generate Your Personalised Roadmap
            </h2>
            <p className="text-zinc-600 text-sm">
              Tell us your goal and skill level — our AI will create a week-by-week study plan tailored to you.
            </p>
          </div>
          <Link href="/roadmap" style={{ textDecoration: "none" }}>
            <Button rightIcon={<ArrowRight className="w-4 h-4" />}>
              Build My Roadmap
            </Button>
          </Link>
        </motion.div>
      )}

      {/* Stats Grid */}
      {stats && !noRoadmap && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              icon={BookOpen} label="Topics Completed"
              value={`${stats.completed_topics}/${stats.total_topics}`}
              accentClass="bg-primary-100 text-primary-600"
            />
            <StatCard
              icon={ClipboardCheck} label="Avg Quiz Score"
              value={`${stats.average_quiz_score.toFixed(1)}%`}
              sub={`${stats.total_quiz_attempts} attempts`}
              accentClass="bg-emerald-100 text-emerald-600"
            />
            <StatCard
              icon={TrendingUp} label="Progress"
              value={`${stats.completion_percentage}%`}
              accentClass="bg-amber-100 text-amber-600"
            />
            <StatCard
              icon={Zap} label="Roadmap Status"
              value={stats.roadmap_status ?? "—"}
              accentClass="bg-rose-100 text-rose-600"
            />
          </div>

          {/* Progress ring + Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="flex flex-col items-center justify-center py-8 col-span-1">
              <ProgressRing pct={stats.completion_percentage} />
              <p className="text-sm text-zinc-500 mt-4 text-center font-medium">{stats.roadmap_title}</p>
              {stats.roadmap_status && (
                <Badge variant={stats.roadmap_status === "completed" ? "success" : "default"} className="mt-3 capitalize">
                  {stats.roadmap_status}
                </Badge>
              )}
            </Card>

            <Card className="col-span-2 flex flex-col justify-between">
              <div className="space-y-3">
                <h2 className="font-display text-lg font-bold text-black">Quick Actions</h2>
                {[
                  { href: "/roadmap", icon: BookOpen, label: "Continue Learning", sub: "View your roadmap & topics" },
                  { href: "/progress", icon: TrendingUp, label: "Knowledge Map", sub: "Track your BKT mastery scores" },
                ].map(({ href, icon: Icon, label, sub }) => (
                  <Link key={href} href={href} style={{ textDecoration: "none" }}
                    className="flex items-center gap-4 p-4 rounded-xl hover:bg-zinc-50 border border-transparent hover:border-zinc-200 transition group"
                  >
                    <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center group-hover:bg-primary-200 transition">
                      <Icon className="w-5 h-5 text-primary-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-black">{label}</p>
                      <p className="text-xs text-zinc-500">{sub}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-zinc-300 group-hover:text-black transition" />
                  </Link>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
