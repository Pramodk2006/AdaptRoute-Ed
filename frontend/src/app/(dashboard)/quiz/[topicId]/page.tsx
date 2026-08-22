"use client";

import { useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { ClipboardCheck, Timer, ChevronRight, ArrowLeft, Sparkles } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import { Quiz, QuizAttemptResult } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

export default function QuizPage() {
  const { topicId } = useParams<{ topicId: string }>();
  const router = useRouter();
  const qc = useQueryClient();
  const startTime = useRef(Date.now());

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentQ, setCurrentQ] = useState(0);

  const { data: quiz, isLoading, isError } = useQuery({
    queryKey: ["quiz", topicId],
    queryFn: () => api.get<Quiz>(`/quiz/${topicId}`).then((r) => r.data),
    retry: false,
  });

  const generateMutation = useMutation({
    mutationFn: () => api.post<Quiz>(`/quiz/generate/${topicId}`).then((r) => r.data),
    onSuccess: (newQuiz) => {
      qc.setQueryData(["quiz", topicId], newQuiz);
      qc.invalidateQueries({ queryKey: ["quiz", topicId] });
    },
  });

  const submitMutation = useMutation({
    mutationFn: (payload: { answers: { question_id: string; given_answer: string }[]; time_taken_seconds: number }) =>
      api.post<QuizAttemptResult>(`/quiz/${quiz!.id}/submit`, payload).then((r) => r.data),
    onSuccess: (result) => {
      router.push(`/results/${result.id}`);
    },
  });

  const questions = quiz?.questions ?? [];
  const q = questions[currentQ];

  const handleAnswer = (label: string) => {
    setAnswers((prev) => ({ ...prev, [q.id]: label }));
  };

  const handleSubmit = () => {
    const elapsed = Math.round((Date.now() - startTime.current) / 1000);
    submitMutation.mutate({
      answers: Object.entries(answers).map(([question_id, given_answer]) => ({
        question_id,
        given_answer,
      })),
      time_taken_seconds: elapsed,
    });
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Spinner size="lg" /></div>;
  }

  // No quiz yet
  if (isError || !quiz) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Link href={`/topic/${topicId}`} className="inline-flex items-center gap-1.5 text-sm font-semibold text-zinc-600 hover:text-black transition" style={{ textDecoration: "none" }}>
          <ArrowLeft className="w-4 h-4" /> Back to Topic
        </Link>
        <Card className="text-center py-12">
          <ClipboardCheck className="w-10 h-10 text-primary-600 mx-auto mb-4" />
          <h2 className="font-display text-xl font-bold text-black mb-2">No Quiz Yet</h2>
          <p className="text-zinc-500 text-sm mb-6">Generate an AI-powered MCQ quiz for this topic.</p>
          {generateMutation.isError && (
            <p className="text-red-600 text-sm mb-4 font-medium">Failed to generate. Please retry.</p>
          )}
          <Button
            leftIcon={<Sparkles className="w-4 h-4" />}
            onClick={() => generateMutation.mutate()}
            isLoading={generateMutation.isPending}
          >
            Generate Quiz
          </Button>
        </Card>
      </div>
    );
  }

  if (generateMutation.isPending) {
    return (
      <Card className="text-center py-16 max-w-2xl mx-auto">
        <Spinner size="lg" className="mx-auto mb-4" />
        <p className="text-black font-semibold">Generating quiz questions…</p>
        <p className="text-zinc-500 text-sm mt-1">This may take 20–60 seconds.</p>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link href={`/topic/${topicId}`} className="inline-flex items-center gap-1.5 text-sm font-semibold text-zinc-600 hover:text-black transition" style={{ textDecoration: "none" }}>
        <ArrowLeft className="w-4 h-4" /> Back to Topic
      </Link>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-black">{quiz.title}</h1>
          <p className="text-zinc-500 text-sm mt-1">
            Question {currentQ + 1} of {questions.length} · Pass: {quiz.pass_percentage}%
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-zinc-500 text-sm font-medium">
          <Timer className="w-4 h-4" />
          <span>Timed</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 rounded-full bg-zinc-100 overflow-hidden">
        <div
          className="h-full rounded-full bg-primary-600 transition-all duration-300"
          style={{ width: `${((currentQ + 1) / questions.length) * 100}%` }}
        />
      </div>

      {/* Question card */}
      {q && (
        <AnimatePresence mode="wait">
          <motion.div
            key={q.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.25 }}
          >
            <Card>
              <p className="font-bold text-black text-lg mb-6 leading-relaxed">
                {q.question_text}
              </p>
              <div className="space-y-3">
                {(q.options ?? []).map((opt) => {
                  const selected = answers[q.id] === opt.label;
                  return (
                    <button
                      key={opt.label}
                      onClick={() => handleAnswer(opt.label)}
                      className={`w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all text-left font-medium
                        ${selected
                          ? "bg-primary-50 border-primary-600 text-black"
                          : "border-zinc-200 hover:border-zinc-400 hover:bg-zinc-50 text-zinc-800"
                        }`}
                    >
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold shrink-0 ${selected ? "bg-primary-600 text-white" : "bg-zinc-100 text-zinc-700"}`}>
                        {opt.label}
                      </span>
                      <span className="text-sm">{opt.text}</span>
                    </button>
                  );
                })}
              </div>
            </Card>
          </motion.div>
        </AnimatePresence>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost" size="sm"
          onClick={() => setCurrentQ((i) => i - 1)}
          disabled={currentQ === 0}
        >
          Previous
        </Button>

        {currentQ < questions.length - 1 ? (
          <Button
            size="sm"
            onClick={() => setCurrentQ((i) => i + 1)}
            disabled={!answers[q?.id]}
            rightIcon={<ChevronRight className="w-4 h-4" />}
          >
            Next
          </Button>
        ) : (
          <Button
            size="sm"
            onClick={handleSubmit}
            isLoading={submitMutation.isPending}
            disabled={Object.keys(answers).length < questions.length}
          >
            Submit Quiz
          </Button>
        )}
      </div>

      {/* Answer progress */}
      <p className="text-center text-xs text-zinc-500 font-medium">
        {Object.keys(answers).length} / {questions.length} answered
      </p>
    </div>
  );
}
