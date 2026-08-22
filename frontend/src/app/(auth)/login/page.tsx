"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { Brain, Mail, Lock, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, Suspense } from "react";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

function LoginPageContent() {
  const router = useRouter();
  const { login, isLoginPending, loginError, isAuthenticated, logout } = useAuth();
  const searchParams = useSearchParams();
  const justRegistered = searchParams.get("registered") === "true";
  const didLogoutRef = useRef(false);

  useEffect(() => {
    if (justRegistered && !didLogoutRef.current) {
      didLogoutRef.current = true;
      logout();
    } else if (isAuthenticated && !justRegistered) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, justRegistered, router, logout]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });

  const onSubmit = (data: LoginForm) => login(data);

  const errorMessage =
    loginError && "response" in loginError
      ? ((loginError as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? "Login failed. Please try again.")
      : null;

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex w-1/2 bg-black flex-col justify-center px-16">
        <div className="w-12 h-12 rounded-xl bg-primary-600 flex items-center justify-center mb-8">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <h2 className="font-display text-4xl font-bold text-white leading-tight mb-4">
          Your personalised<br />AI tutor awaits.
        </h2>
        <p className="text-zinc-400 text-lg leading-relaxed">
          Adaptive roadmaps, smart quizzes, and real-time knowledge tracking — all powered by on-device AI.
        </p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-sm"
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-10">
            <div className="w-9 h-9 rounded-xl bg-primary-600 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-bold text-xl text-black">AdaptRoute-Edu</span>
          </div>

          <h1 className="font-display text-3xl font-bold text-black mb-2">
            Welcome back
          </h1>
          <p className="text-zinc-500 text-sm mb-8">Sign in to continue learning.</p>

          {/* Success banner */}
          {justRegistered && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mb-5 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-sm"
            >
              ✓ Account created! Please sign in.
            </motion.div>
          )}

          {/* Error */}
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mb-5 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2"
            >
              <AlertCircle className="w-4 h-4 shrink-0" />
              {errorMessage}
            </motion.div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-black mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  className="input-base pl-10"
                  {...register("email")}
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-black mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="input-base pl-10"
                  {...register("password")}
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full mt-2"
              isLoading={isLoginPending}
            >
              Sign In
            </Button>
          </form>

          <p className="text-center text-sm text-zinc-500 mt-6">
            No account?{" "}
            <Link href="/register" className="font-semibold text-primary-600 hover:underline">
              Create one free
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginPageContent />
    </Suspense>
  );
}
