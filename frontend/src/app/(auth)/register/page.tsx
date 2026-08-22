"use client";

import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { Brain, Mail, Lock, User, ArrowRight, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

const registerSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  username: z
    .string()
    .min(3, "Username must be at least 3 characters")
    .max(100)
    .regex(/^[a-zA-Z0-9_]+$/, "Only letters, numbers and underscores allowed"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Must contain at least one uppercase letter")
    .regex(/[0-9]/, "Must contain at least one number"),
  confirmPassword: z.string(),
}).refine((d) => d.password === d.confirmPassword, {
  message: "Passwords do not match",
  path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

const steps = [
  "Set your learning goal",
  "Get an AI-generated roadmap",
  "Study with smart content",
  "Track mastery with BKT",
];

export default function RegisterPage() {
  const { register: registerUser, isRegisterPending, registerError } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  const onSubmit = ({ email, username, password }: RegisterForm) =>
    registerUser({ email, username, password });

  const errorMessage =
    registerError && "response" in registerError
      ? ((registerError as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? "Registration failed.")
      : null;

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left panel — value prop */}
      <div className="hidden lg:flex w-2/5 bg-primary-600 flex-col justify-center px-14">
        <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-10">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <h2 className="font-display text-4xl font-bold text-white leading-tight mb-6">
          Start your adaptive learning journey.
        </h2>
        <p className="text-primary-100 text-base mb-10">
          Free forever. No credit card required. AI-powered — runs on your hardware.
        </p>
        <div className="space-y-3">
          {steps.map((s, i) => (
            <div key={i} className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-primary-200 shrink-0" />
              <span className="text-white text-sm font-medium">{s}</span>
            </div>
          ))}
        </div>
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
            Create your account
          </h1>
          <p className="text-zinc-500 text-sm mb-8">Start learning for free today.</p>

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
            <div>
              <label htmlFor="reg-email" className="block text-sm font-semibold text-black mb-1.5">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                <input
                  id="reg-email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  className="input-base pl-10"
                  {...register("email")}
                />
              </div>
              {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>

            <div>
              <label htmlFor="reg-username" className="block text-sm font-semibold text-black mb-1.5">Username</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                <input
                  id="reg-username"
                  type="text"
                  autoComplete="username"
                  placeholder="john_doe"
                  className="input-base pl-10"
                  {...register("username")}
                />
              </div>
              {errors.username && <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>}
            </div>

            <div>
              <label htmlFor="reg-password" className="block text-sm font-semibold text-black mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                <input
                  id="reg-password"
                  type="password"
                  autoComplete="new-password"
                  placeholder="Min 8 chars, 1 uppercase, 1 number"
                  className="input-base pl-10"
                  {...register("password")}
                />
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
            </div>

            <div>
              <label htmlFor="reg-confirm-password" className="block text-sm font-semibold text-black mb-1.5">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
                <input
                  id="reg-confirm-password"
                  type="password"
                  autoComplete="new-password"
                  placeholder="••••••••"
                  className="input-base pl-10"
                  {...register("confirmPassword")}
                />
              </div>
              {errors.confirmPassword && <p className="mt-1 text-xs text-red-600">{errors.confirmPassword.message}</p>}
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full mt-2"
              isLoading={isRegisterPending}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Create Account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-zinc-500">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-primary-600 hover:underline">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
