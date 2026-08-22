"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { User, Target, Clock, Zap, CheckCircle2 } from "lucide-react";
import api from "@/lib/api";
import { LearnerProfile } from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";

const schema = z.object({
  full_name: z.string().min(2, "Full name is required"),
  skill_level: z.enum(["beginner", "intermediate", "advanced"]),
  learning_goal: z.string().min(10, "Describe your goal in at least 10 characters"),
  preferred_pace: z.enum(["slow", "moderate", "fast"]),
  daily_study_time: z.coerce.number().min(15).max(480),
});
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const profileResolver = zodResolver(schema) as any;
type ProfileForm = z.infer<typeof schema>;

export default function ProfilePage() {
  const router = useRouter();
  const qc = useQueryClient();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => api.get<LearnerProfile>("/profile").then((r) => r.data),
    retry: false,
  });

  const {
    register, handleSubmit, formState: { errors },
  } = useForm<ProfileForm>({
    resolver: profileResolver,
    values: profile
      ? {
          full_name: profile.full_name,
          skill_level: profile.skill_level,
          learning_goal: profile.learning_goal,
          preferred_pace: profile.preferred_pace,
          daily_study_time: profile.daily_study_time,
        }
      : undefined,
  });

  const mutation = useMutation({
    mutationFn: (data: ProfileForm) =>
      profile
        ? api.put("/profile", data)
        : api.post("/profile", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      qc.invalidateQueries({ queryKey: ["me"] });
      router.push("/dashboard");
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="font-display text-3xl font-bold text-black">
          {profile ? "Update" : "Set Up"} Your Learner Profile
        </h1>
        <p className="text-zinc-500 mt-1 text-sm">
          This information is used to personalise your AI-generated roadmap and study materials.
        </p>
      </motion.div>

      <Card>
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-6" noValidate>
          {/* Full name */}
          <div>
            <label className="block text-sm font-semibold text-black mb-1.5">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
              <input type="text" className="input-base pl-10" placeholder="Your name" {...register("full_name")} />
            </div>
            {errors.full_name && <p className="mt-1 text-xs text-red-600">{errors.full_name.message}</p>}
          </div>

          {/* Learning goal */}
          <div>
            <label className="block text-sm font-semibold text-black mb-1.5">
              <Target className="inline w-4 h-4 mr-1 text-primary-600" />
              Learning Goal
            </label>
            <textarea
              className="input-base min-h-[90px] resize-none"
              placeholder="e.g. Master Python programming for data science"
              {...register("learning_goal")}
            />
            {errors.learning_goal && <p className="mt-1 text-xs text-red-600">{errors.learning_goal.message}</p>}
          </div>

          {/* Skill level */}
          <div>
            <label className="block text-sm font-semibold text-black mb-2">Current Skill Level</label>
            <div className="grid grid-cols-3 gap-3">
              {(["beginner", "intermediate", "advanced"] as const).map((level) => (
                <label key={level} className="relative cursor-pointer">
                  <input type="radio" value={level} {...register("skill_level")} className="sr-only peer" />
                  <div className="p-3 text-center rounded-xl text-sm font-medium capitalize border border-zinc-200 text-zinc-700 bg-white peer-checked:bg-primary-50 peer-checked:border-primary-500 peer-checked:text-primary-700 transition hover:bg-zinc-50">
                    {level}
                  </div>
                </label>
              ))}
            </div>
            {errors.skill_level && <p className="mt-1 text-xs text-red-600">{errors.skill_level.message}</p>}
          </div>

          {/* Preferred pace */}
          <div>
            <label className="block text-sm font-semibold text-black mb-2">
              <Zap className="inline w-4 h-4 mr-1 text-amber-500" />
              Preferred Learning Pace
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { val: "slow", label: "Slow", sub: "Fewer topics/week" },
                { val: "moderate", label: "Moderate", sub: "Balanced" },
                { val: "fast", label: "Fast", sub: "More topics/week" },
              ].map(({ val, label, sub }) => (
                <label key={val} className="relative cursor-pointer">
                  <input type="radio" value={val} {...register("preferred_pace")} className="sr-only peer" />
                  <div className="p-3 text-center rounded-xl border border-zinc-200 bg-white text-zinc-700 peer-checked:bg-primary-50 peer-checked:border-primary-500 peer-checked:text-primary-700 transition hover:bg-zinc-50">
                    <p className="text-sm font-semibold">{label}</p>
                    <p className="text-xs text-zinc-400 mt-0.5">{sub}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Daily study time */}
          <div>
            <label className="block text-sm font-semibold text-black mb-1.5">
              <Clock className="inline w-4 h-4 mr-1 text-primary-600" />
              Daily Study Time (minutes)
            </label>
            <input
              type="number" min="15" max="480" step="15"
              className="input-base"
              placeholder="e.g. 60"
              {...register("daily_study_time")}
            />
            {errors.daily_study_time && <p className="mt-1 text-xs text-red-600">{errors.daily_study_time.message}</p>}
          </div>

          {mutation.isError && (
            <p className="text-sm text-red-600 font-medium">
              {(mutation.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Something went wrong."}
            </p>
          )}

          <Button type="submit" size="lg" className="w-full" isLoading={mutation.isPending}
            rightIcon={<CheckCircle2 className="w-4 h-4" />}>
            {profile ? "Save Changes" : "Save Profile & Continue"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
