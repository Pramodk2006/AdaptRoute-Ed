"use client";

import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Brain, TrendingUp, AlertTriangle, CheckCircle, Target, BookOpen } from "lucide-react";
import api from "@/lib/api";
import { MasteryStats, MasteryLevel } from "@/lib/types";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";

const LEVEL_CONFIG: Record<
  MasteryLevel,
  { label: string; textColor: string; barColor: string; badgeVariant: "success" | "default" | "warning" | "danger"; icon: React.ElementType; bgColor: string }
> = {
  mastered:   { label: "Mastered",   textColor: "text-emerald-700", barColor: "bg-emerald-500", badgeVariant: "success", icon: CheckCircle, bgColor: "bg-emerald-50" },
  proficient: { label: "Proficient", textColor: "text-blue-700",    barColor: "bg-blue-500",    badgeVariant: "default", icon: TrendingUp,  bgColor: "bg-blue-50" },
  developing: { label: "Developing", textColor: "text-amber-700",   barColor: "bg-amber-500",   badgeVariant: "warning", icon: Target,       bgColor: "bg-amber-50" },
  struggling: { label: "Struggling", textColor: "text-red-700",     barColor: "bg-red-500",     badgeVariant: "danger",  icon: AlertTriangle, bgColor: "bg-red-50" },
};

function MasteryBar({ score, level }: { score: number; level: MasteryLevel }) {
  const cfg = LEVEL_CONFIG[level];
  return (
    <div className="w-full h-2.5 rounded-full bg-zinc-100 overflow-hidden">
      <motion.div
        className={`h-full rounded-full ${cfg.barColor}`}
        initial={{ width: 0 }}
        animate={{ width: `${score * 100}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />
    </div>
  );
}

function StatCard({
  title, value, subtitle, icon: Icon, bgClass, textClass,
}: {
  title: string; value: string | number; subtitle?: string;
  icon: React.ElementType; bgClass: string; textClass: string;
}) {
  return (
    <Card className="flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${bgClass}`}>
        <Icon className={`w-6 h-6 ${textClass}`} />
      </div>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-zinc-400">{title}</p>
        <p className="font-display text-2xl font-bold text-black">{value}</p>
        {subtitle && <p className="text-xs text-zinc-500">{subtitle}</p>}
      </div>
    </Card>
  );
}

export default function ProgressPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["mastery"],
    queryFn: () => api.get<MasteryStats>("/knowledge/mastery").then((r) => r.data),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const topics = data?.topic_details ?? [];
  const hasData = topics.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-display text-3xl font-bold text-black">
          Knowledge Mastery Map
        </h1>
        <p className="text-zinc-500 mt-1 text-sm">
          Real-time BKT (Bayesian Knowledge Tracing) estimates of your concept mastery across all topics.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Overall Readiness"
          value={`${data?.overall_readiness ?? 0}%`}
          icon={Brain}
          bgClass="bg-primary-100" textClass="text-primary-600"
        />
        <StatCard
          title="Topics Mastered"
          value={data?.mastered_count ?? 0}
          subtitle={`of ${data?.topics_tracked ?? 0} tracked`}
          icon={CheckCircle}
          bgClass="bg-emerald-100" textClass="text-emerald-600"
        />
        <StatCard
          title="Avg Mastery Score"
          value={((data?.avg_mastery ?? 0) * 100).toFixed(1) + "%"}
          icon={TrendingUp}
          bgClass="bg-blue-100" textClass="text-blue-600"
        />
        <StatCard
          title="Needs Attention"
          value={data?.struggling_count ?? 0}
          subtitle="topics below threshold"
          icon={AlertTriangle}
          bgClass="bg-red-100" textClass="text-red-600"
        />
      </div>

      {/* Mastery Level Distribution */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {(["mastered", "proficient", "developing", "struggling"] as MasteryLevel[]).map((lvl) => {
          const cfg = LEVEL_CONFIG[lvl];
          const key = `${lvl}_count` as keyof MasteryStats;
          const count = (data?.[key] as number) ?? 0;
          const total = data?.topics_tracked ?? 1;
          const pct = total ? Math.round((count / total) * 100) : 0;
          return (
            <Card key={lvl} className={`text-center space-y-2 ${cfg.bgColor} border-0`}>
              <cfg.icon className={`w-6 h-6 mx-auto ${cfg.textColor}`} />
              <p className={`font-semibold text-sm ${cfg.textColor}`}>{cfg.label}</p>
              <p className="font-display text-3xl font-bold text-black">{count}</p>
              <p className="text-xs text-zinc-500">{pct}% of topics</p>
            </Card>
          );
        })}
      </div>

      {/* Topic-Level Mastery Heatmap */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary-600" /> Topic Mastery Heat Map
          </CardTitle>
        </CardHeader>

        {!hasData ? (
          <div className="py-12 text-center space-y-3">
            <Brain className="w-12 h-12 text-zinc-300 mx-auto" />
            <p className="text-zinc-500 text-sm">
              No mastery data yet. Complete quiz attempts to start tracking your knowledge!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {topics.map((t, i) => {
              const cfg = LEVEL_CONFIG[t.mastery_level];
              return (
                <motion.div
                  key={t.topic_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="p-4 rounded-xl bg-zinc-50 border border-zinc-200 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <cfg.icon className={`w-4 h-4 shrink-0 ${cfg.textColor}`} />
                      <span className="text-sm font-semibold text-black truncate">
                        Topic: {t.topic_id.slice(0, 8)}…
                      </span>
                    </div>
                    <div className="flex items-center gap-3 shrink-0 ml-3">
                      <span className="text-xs text-zinc-500">
                        {t.correct_count}/{t.attempts_count} ({t.accuracy_pct}%)
                      </span>
                      <Badge variant={cfg.badgeVariant}>{cfg.label}</Badge>
                      <span className={`font-mono text-sm font-bold ${cfg.textColor}`}>
                        {(t.mastery_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <MasteryBar score={t.mastery_score} level={t.mastery_level} />
                </motion.div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
