"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Trophy, ArrowLeft } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import { QuizAttemptResult } from "@/lib/types";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";

export default function ResultsPage() {
  const { attemptId } = useParams<{ attemptId: string }>();

  const { data: attempt, isLoading } = useQuery({
    queryKey: ["attempt", attemptId],
    queryFn: () =>
      api.get<QuizAttemptResult>(`/quiz/attempts/${attemptId}`).then((r) => r.data),
  });

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Spinner size="lg" /></div>;
  }

  if (!attempt) return null;

  const correct = attempt.answers.filter((a) => a.is_correct).length;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link href="/roadmap" className="inline-flex items-center gap-1.5 text-sm font-semibold text-zinc-600 hover:text-black transition" style={{ textDecoration: "none" }}>
        <ArrowLeft className="w-4 h-4" /> Back to Roadmap
      </Link>

      {/* Score card */}
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
        <Card className={`text-center py-10 ${attempt.passed ? "border-emerald-200" : "border-red-200"}`}>
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${attempt.passed ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-600"}`}>
            <Trophy className="w-10 h-10" />
          </div>

          <h1 className="font-display text-4xl font-bold text-black mb-1">
            {attempt.percentage.toFixed(0)}%
          </h1>
          <p className="text-zinc-500 text-sm mb-4">
            {correct} correct out of {attempt.answers.length} questions
          </p>

          <Badge variant={attempt.passed ? "success" : "danger"} className="text-sm px-3 py-1">
            {attempt.passed ? "✓ Passed" : "✗ Failed"}
          </Badge>

          {attempt.time_taken_seconds && (
            <p className="text-xs text-zinc-400 mt-3">
              Completed in {Math.round(attempt.time_taken_seconds / 60)} min {attempt.time_taken_seconds % 60}s
            </p>
          )}
        </Card>
      </motion.div>

      {/* Answer breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Answer Breakdown</CardTitle>
        </CardHeader>
        <div className="space-y-4">
          {attempt.answers.map((ans, i) => (
            <motion.div
              key={ans.question_id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`p-4 rounded-xl border ${ans.is_correct ? "border-emerald-200 bg-emerald-50/50" : "border-red-200 bg-red-50/50"}`}
            >
              <div className="flex items-start gap-3">
                {ans.is_correct ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="text-sm font-bold text-black">Question {i + 1}</p>
                  <div className="mt-2 flex gap-4 text-xs font-medium">
                    <span className="text-zinc-600">
                      Your answer: <span className={`font-bold ${ans.is_correct ? "text-emerald-700" : "text-red-700"}`}>
                        {ans.given_answer || "—"}
                      </span>
                    </span>
                    {!ans.is_correct && (
                      <span className="text-zinc-600">
                        Correct: <span className="text-emerald-700 font-bold">{ans.correct_answer}</span>
                      </span>
                    )}
                  </div>
                  {ans.explanation && !ans.is_correct && (
                    <p className="mt-2 text-xs text-zinc-600 leading-relaxed bg-white p-2.5 rounded-lg border border-zinc-200">
                      💡 {ans.explanation}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Link href="/roadmap" className="flex-1" style={{ textDecoration: "none" }}>
          <Button variant="secondary" className="w-full">Back to Roadmap</Button>
        </Link>
        <Link href="/dashboard" className="flex-1" style={{ textDecoration: "none" }}>
          <Button className="w-full">View Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
