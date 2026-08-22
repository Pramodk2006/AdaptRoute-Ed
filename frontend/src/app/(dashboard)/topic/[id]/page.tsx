"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { BookOpen, FileText, Lightbulb, Code2, ClipboardCheck, ArrowLeft, CheckCircle2, Sparkles } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import { TopicContentResponse, Content } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { SocraticChat } from "@/components/SocraticChat";

function ContentSection({ content }: { content: Content }) {
  if (content.content_type === "notes") {
    return (
      <Card className="p-6">
        <CardHeader className="mb-4">
          <CardTitle className="flex items-center gap-2 text-xl font-bold text-black border-b border-zinc-100 pb-3">
            <FileText className="w-5 h-5 text-indigo-600" /> Key Concepts & Learning Objectives
          </CardTitle>
        </CardHeader>
        <ul className="space-y-3">
          {content.body.split("\n").filter(Boolean).map((line, i) => (
            <li key={i} className="flex items-start gap-3 text-sm font-medium text-black leading-relaxed p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <span className="text-indigo-600 mt-0.5 font-bold shrink-0">•</span>
              <span>{line.replace(/^•\s*/, "")}</span>
            </li>
          ))}
        </ul>
      </Card>
    );
  }

  if (content.content_type === "explanation") {
    return (
      <Card className="p-6">
        <CardHeader className="mb-4">
          <CardTitle className="flex items-center gap-2 text-xl font-bold text-black border-b border-zinc-100 pb-3">
            <Lightbulb className="w-5 h-5 text-amber-500" /> Low-Level Mechanics & Execution Analysis
          </CardTitle>
        </CardHeader>
        <div className="text-sm font-normal text-zinc-900 leading-relaxed space-y-4 whitespace-pre-line">
          {content.body}
        </div>
      </Card>
    );
  }

  if (content.content_type === "example") {
    let parsed: { title?: string; content?: string; language?: string } = {};
    try { parsed = JSON.parse(content.body); } catch { parsed = { content: content.body }; }
    return (
      <Card className="p-6">
        <CardHeader className="mb-4 flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-xl font-bold text-black">
            <Code2 className="w-5 h-5 text-emerald-600" />
            {parsed.title || "Annotated Production Code Example"}
          </CardTitle>
          {parsed.language && (
            <span className="text-xs font-mono font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-zinc-100 text-zinc-700">
              {parsed.language}
            </span>
          )}
        </CardHeader>
        <div className="relative rounded-xl overflow-hidden border border-zinc-800 bg-zinc-950">
          <div className="flex items-center justify-between px-4 py-2 bg-zinc-900 border-b border-zinc-800 text-xs font-mono text-zinc-400">
            <span>Source Code</span>
            <span>UTF-8</span>
          </div>
          <pre className="p-5 overflow-x-auto text-sm text-emerald-400 font-mono leading-relaxed">
            <code>{parsed.content}</code>
          </pre>
        </div>
      </Card>
    );
  }

  return null;
}

export default function TopicPage() {
  const { id } = useParams<{ id: string }>();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["topic-content", id],
    queryFn: () =>
      api.get<TopicContentResponse>(`/content/${id}`).then((r) => r.data),
    retry: 1,
    staleTime: 5 * 60 * 1000,
  });

  const [streamContentText, setStreamContentText] = useState("");
  const [isStreamingContent, setIsStreamingContent] = useState(false);

  const handleGenerateStream = async () => {
    if (isStreamingContent) return;
    setIsStreamingContent(true);
    setStreamContentText("");

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const response = await fetch(`http://localhost:8000/api/v1/content/generate/stream/${id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
      });

      if (!response.ok || !response.body) {
        throw new Error(`Stream HTTP error: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let accumulated = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        setStreamContentText(accumulated);
      }

      // Persist structured study guide after streaming completes
      await api.post(`/content/generate/${id}`).catch(() => {});
    } catch (err) {
      console.warn("Streaming fetch warning, invoking direct generator fallback:", err);
      const res = await api.post<TopicContentResponse>(`/content/generate/${id}`);
      if (res?.data) {
        qc.setQueryData(["topic-content", id], res.data);
      }
    } finally {
      setIsStreamingContent(false);
      qc.invalidateQueries({ queryKey: ["topic-content", id] });
    }
  };

  useEffect(() => {
    if (!isLoading && data && data.contents.length === 0 && !isStreamingContent && !streamContentText) {
      handleGenerateStream();
    }
  }, [data, isLoading]);

  const generateMutation = useMutation({
    mutationFn: () => handleGenerateStream(),
  });

  const completeMutation = useMutation({
    mutationFn: () => api.put(`/topics/${id}/complete`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["roadmap"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const topic = data?.topic;
  const contents = data?.contents ?? [];

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Back link */}
      <Link href="/roadmap" className="inline-flex items-center gap-1.5 text-sm font-semibold text-zinc-600 hover:text-black transition" style={{ textDecoration: "none" }}>
        <ArrowLeft className="w-4 h-4" /> Back to Roadmap
      </Link>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-zinc-400 mb-1">
              <BookOpen className="w-3.5 h-3.5" /> Week {topic?.week_number}
            </div>
            <h1 className="font-display text-3xl font-bold text-black">{topic?.title}</h1>
            {topic?.description && (
              <p className="text-zinc-500 mt-2 text-sm">{topic.description}</p>
            )}
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {topic?.is_completed && (
              <span className="flex items-center gap-1 text-emerald-600 text-sm font-semibold mr-2">
                <CheckCircle2 className="w-4 h-4" /> Completed
              </span>
            )}
            <Button
              size="sm"
              variant="secondary"
              leftIcon={<BookOpen className="w-3.5 h-3.5" />}
              onClick={() => generateMutation.mutate()}
              isLoading={generateMutation.isPending}
            >
              Regenerate Content
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Streaming Live Content Banner */}
      {(isStreamingContent || streamContentText) && (
        <Card className="p-5 border-2 border-primary-500 bg-primary-50/50 shadow-md">
          <div className="flex items-center gap-2 mb-3 text-primary-700 font-bold text-sm">
            <Sparkles className="w-4 h-4 animate-spin text-primary-600" />
            <span>Generating Real-Time Study Content... (Live AI Token Stream)</span>
          </div>
          <div className="font-mono text-xs leading-relaxed text-zinc-800 whitespace-pre-wrap max-h-60 overflow-y-auto bg-white p-4 rounded-xl border border-zinc-200">
            {streamContentText || "Connecting to Gemma 3 AI Model..."}
          </div>
        </Card>
      )}

      {/* No content yet */}
      {contents.length === 0 && !generateMutation.isPending && (
        <Card className="text-center py-12">
          <BookOpen className="w-10 h-10 text-primary-600 mx-auto mb-4" />
          <h2 className="font-display text-lg font-bold text-black mb-2">Content Not Generated Yet</h2>
          <p className="text-zinc-500 text-sm mb-6">
            Click below to generate AI-powered study notes, explanations, and examples.
          </p>
          <Button
            leftIcon={<BookOpen className="w-4 h-4" />}
            onClick={() => generateMutation.mutate()}
            isLoading={generateMutation.isPending}
          >
            Generate Study Content
          </Button>
        </Card>
      )}

      {generateMutation.isPending && (
        <Card className="text-center py-12">
          <Spinner size="lg" className="mx-auto mb-4" />
          <p className="text-black font-semibold">Generating content…</p>
          <p className="text-zinc-500 text-sm mt-1">This may take 20–60 seconds.</p>
        </Card>
      )}

      {/* Content sections */}
      {contents.length > 0 && (
        <>
          {contents.map((c) => (
            <motion.div key={c.id} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
              <ContentSection content={c} />
            </motion.div>
          ))}

          {/* Interactive Socratic Dialogue Agent */}
          <SocraticChat topicTitle={topic?.title || "Topic"} />

          {/* Action bar */}
          <div className="flex items-center justify-between pt-4">
            {!topic?.is_completed && (
              <Button
                variant="accent"
                leftIcon={<CheckCircle2 className="w-4 h-4" />}
                onClick={() => completeMutation.mutate()}
                isLoading={completeMutation.isPending}
              >
                Mark as Complete
              </Button>
            )}
            <Link href={`/quiz/${id}`} className="ml-auto" style={{ textDecoration: "none" }}>
              <Button rightIcon={<ClipboardCheck className="w-4 h-4" />}>
                Take Quiz
              </Button>
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
