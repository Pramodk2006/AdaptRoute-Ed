"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  BookOpen, Brain, ChartBar, ArrowRight, Sparkles, Route, ClipboardCheck
} from "lucide-react";
import { Button } from "@/components/ui/Button";

const features = [
  {
    icon: Route,
    title: "Personalised Roadmap",
    description:
      "AI generates a weekly study plan tailored to your goal, skill level, and daily study time.",
    iconBg: "bg-primary-100",
    iconColor: "text-primary-600",
  },
  {
    icon: BookOpen,
    title: "AI Study Content",
    description:
      "Get notes, explanations, and real-world examples generated for every topic in your roadmap.",
    iconBg: "bg-emerald-100",
    iconColor: "text-emerald-600",
  },
  {
    icon: ClipboardCheck,
    title: "Smart Quizzes",
    description:
      "Test your understanding with LLM-generated MCQs. Get instant feedback and explanations.",
    iconBg: "bg-amber-100",
    iconColor: "text-amber-600",
  },
  {
    icon: ChartBar,
    title: "Progress Tracking",
    description:
      "Visual dashboard showing completed topics, quiz scores, and remaining learning journey.",
    iconBg: "bg-rose-100",
    iconColor: "text-rose-600",
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, delay: i * 0.1 },
  }),
};

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white overflow-hidden">
      {/* ── Nav ─────────────────────────────────────────────── */}
      <nav className="fixed top-0 w-full z-50 bg-white border-b border-zinc-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-lg text-black">
              AdaptRoute-Edu
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" style={{ textDecoration: "none" }}>
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/register" style={{ textDecoration: "none" }}>
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ─────────────────────────────────────────────── */}
      <section className="pt-36 pb-28 px-6 text-center relative">
        {/* Subtle indigo blur behind headline */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-primary-100 rounded-full blur-3xl opacity-60" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 bg-primary-50 border border-primary-200 px-4 py-2 rounded-full text-sm text-primary-700 font-medium mb-8">
            <Sparkles className="w-4 h-4" />
            Powered by Gemma 3 · Adaptive AI Tutoring
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-extrabold leading-tight text-black mb-6">
            Learn Smarter with{" "}
            <span className="gradient-text">AI-Powered</span>{" "}
            Tutoring
          </h1>

          <p className="text-xl text-zinc-600 max-w-2xl mx-auto mb-10 leading-relaxed">
            AdaptRoute-Edu creates a personalised learning roadmap just for you —
            with AI-generated content, smart quizzes, and real-time progress tracking.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register" style={{ textDecoration: "none" }}>
              <Button size="xl" rightIcon={<ArrowRight className="w-5 h-5" />}>
                Start Learning Free
              </Button>
            </Link>
            <Link href="/login" style={{ textDecoration: "none" }}>
              <Button size="xl" variant="secondary">
                Sign In to Dashboard
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ── Features ─────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-6 pb-28">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <h2 className="font-display text-3xl md:text-4xl font-bold text-black mb-4">
            Everything you need to master any subject
          </h2>
          <p className="text-zinc-600 text-lg max-w-xl mx-auto">
            One platform, completely driven by AI — from planning to testing.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feat, i) => (
            <motion.div
              key={feat.title}
              custom={i}
              variants={fadeUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="bg-white border border-zinc-200 rounded-2xl p-6 shadow-card card-hover flex flex-col gap-4"
            >
              <div className={`w-11 h-11 rounded-xl ${feat.iconBg} flex items-center justify-center`}>
                <feat.icon className={`w-5 h-5 ${feat.iconColor}`} />
              </div>
              <div>
                <h3 className="font-display font-bold text-black mb-2">
                  {feat.title}
                </h3>
                <p className="text-sm text-zinc-600 leading-relaxed">
                  {feat.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ───────────────────────────────────────── */}
      <section className="px-6 pb-28 bg-zinc-50 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto bg-white border-2 border-black p-12 text-center rounded-3xl shadow-card-md"
        >
          <div className="w-14 h-14 rounded-2xl bg-primary-600 flex items-center justify-center mx-auto mb-5 shadow-glow-sm">
            <Brain className="w-7 h-7 text-white" />
          </div>
          <h2 className="font-display text-3xl font-bold text-black mb-4">
            Ready to start your adaptive journey?
          </h2>
          <p className="text-zinc-600 mb-8 text-lg">
            Create your profile, set your learning goal, and let AI do the rest.
          </p>
          <Link href="/register" style={{ textDecoration: "none" }}>
            <Button size="xl" rightIcon={<ArrowRight className="w-5 h-5" />}>
              Create Your Account
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* ── Footer ───────────────────────────────────────────── */}
      <footer className="border-t border-zinc-200 bg-white py-8 text-center">
        <p className="text-zinc-500 text-sm">© 2026 AdaptRoute-Edu · B.Tech Final Year Project</p>
      </footer>
    </main>
  );
}
