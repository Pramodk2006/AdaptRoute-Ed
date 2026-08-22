"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Route, Sparkles, ChevronDown, ChevronRight,
  CheckCircle2, Circle, BookOpen, ClipboardCheck, Loader2
} from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import { Roadmap, Topic } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";

function TopicRow({ topic }: { topic: Topic }) {
  const qc = useQueryClient();
  const completeMutation = useMutation({
    mutationFn: () => api.put(`/topics/${topic.id}/complete`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["roadmap"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  return (
    <div className="flex items-center gap-3 py-3 px-4 rounded-xl hover:bg-zinc-50 group transition border border-transparent hover:border-zinc-100">
      <button
        onClick={() => !topic.is_completed && completeMutation.mutate()}
        disabled={topic.is_completed || completeMutation.isPending}
        className="shrink-0 text-zinc-300 hover:text-emerald-500 transition"
      >
        {completeMutation.isPending ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : topic.is_completed ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
        ) : (
          <Circle className="w-5 h-5" />
        )}
      </button>

      <div className="flex-1 min-w-0">
        <p className={`text-sm font-semibold ${topic.is_completed ? "line-through text-zinc-400" : "text-black"}`}>
          {topic.title}
        </p>
        {topic.description && (
          <p className="text-xs text-zinc-500 truncate">{topic.description}</p>
        )}
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <Link href={`/topic/${topic.id}`} style={{ textDecoration: "none" }}>
          <Button size="sm" variant="secondary" leftIcon={<BookOpen className="w-3.5 h-3.5" />}>
            Study
          </Button>
        </Link>
        <Link href={`/quiz/${topic.id}`} style={{ textDecoration: "none" }}>
          <Button size="sm" variant="ghost" leftIcon={<ClipboardCheck className="w-3.5 h-3.5" />}>
            Quiz
          </Button>
        </Link>
      </div>
    </div>
  );
}

function WeekCard({ week, topics }: { week: number; topics: Topic[] }) {
  const [open, setOpen] = useState(week === 1);
  const done = topics.filter((t) => t.is_completed).length;
  const pct = topics.length ? Math.round((done / topics.length) * 100) : 0;

  return (
    <Card className="p-0 overflow-hidden">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-4 p-5 hover:bg-zinc-50 transition text-left"
      >
        <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center shrink-0">
          <span className="font-display text-sm font-bold text-primary-600">W{week}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-black">Week {week}</p>
          <p className="text-xs text-zinc-500">{topics.length} topics · {pct}% done</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-24 h-1.5 rounded-full bg-zinc-100 overflow-hidden">
            <div
              className="h-full rounded-full bg-primary-500 transition-all duration-500"
              style={{ width: `${pct}%` }}
            />
          </div>
          {open ? (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-zinc-400" />
          )}
        </div>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-2 pb-3 border-t border-zinc-100 divide-y divide-zinc-50">
              {topics.map((t) => (
                <TopicRow key={t.id} topic={t} />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

export default function RoadmapPage() {
  const qc = useQueryClient();
  const [numWeeks, setNumWeeks] = useState(8);

  const { data: roadmap, isLoading, isError } = useQuery({
    queryKey: ["roadmap"],
    queryFn: () => api.get<Roadmap>("/roadmap").then((r) => r.data),
    retry: false,
  });

  const generateMutation = useMutation({
    mutationFn: () => api.post<Roadmap>("/roadmap/generate", { num_weeks: numWeeks }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["roadmap"] }),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const hasTopics = roadmap && roadmap.weeks && roadmap.weeks.length > 0;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-black">My Roadmap</h1>
          {hasTopics && (
            <p className="text-zinc-500 mt-1 text-sm">{roadmap.goal}</p>
          )}
        </div>
        {hasTopics && (
          <Badge variant={roadmap.status === "completed" ? "success" : "default"} className="capitalize">
            {roadmap.status}
          </Badge>
        )}
      </motion.div>

      {/* No roadmap or empty topics */}
      {(isError || !hasTopics) && !generateMutation.isPending && (
        <Card className="text-center py-12">
          <Route className="w-12 h-12 text-primary-600 mx-auto mb-4" />
          <h2 className="font-display text-xl font-bold text-black mb-2">
            {roadmap ? "No Topics in Current Roadmap" : "No Roadmap Yet"}
          </h2>
          <p className="text-zinc-500 text-sm mb-6 max-w-sm mx-auto">
            Generate a personalised AI roadmap based on your learner profile.
          </p>

          {generateMutation.isError && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm max-w-md mx-auto space-y-2">
              <p className="font-semibold">
                {(generateMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Failed to generate roadmap. Please retry."}
              </p>
              {(generateMutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail?.includes("profile") && (
                <Link href="/profile" style={{ textDecoration: "none" }}>
                  <Button size="sm" variant="secondary" className="mt-2">
                    Set Up Learner Profile
                  </Button>
                </Link>
              )}
            </div>
          )}

          <div className="flex items-center justify-center gap-3 mb-6">
            <label htmlFor="weeks-select" className="text-sm font-medium text-black">Weeks:</label>
            <select
              id="weeks-select"
              value={numWeeks}
              onChange={(e) => setNumWeeks(Number(e.target.value))}
              className="input-base w-24 py-2"
            >
              {[4, 6, 8, 10, 12].map((w) => (
                <option key={w} value={w}>{w}</option>
              ))}
            </select>
          </div>
          <Button
            size="lg"
            onClick={() => generateMutation.mutate()}
            leftIcon={<Sparkles className="w-4 h-4" />}
            isLoading={generateMutation.isPending}
          >
            {roadmap ? "Regenerate Roadmap" : "Generate My Roadmap"}
          </Button>
        </Card>
      )}

      {/* Generating */}
      {generateMutation.isPending && (
        <Card className="text-center py-16">
          <Spinner size="lg" className="mx-auto mb-4" />
          <p className="text-black font-semibold">AI is building your roadmap…</p>
          <p className="text-zinc-500 text-sm mt-1">This may take 20–60 seconds.</p>
        </Card>
      )}

      {/* Roadmap week timeline */}
      {hasTopics && !generateMutation.isPending && (
        <div className="space-y-3">
          {roadmap.weeks.map(({ week_number, topics }) => (
            <WeekCard key={week_number} week={week_number} topics={topics} />
          ))}
        </div>
      )}
    </div>
  );
}
