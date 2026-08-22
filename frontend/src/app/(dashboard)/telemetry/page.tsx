"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Cpu, Zap, Activity, DollarSign, Layers, ShieldCheck } from "lucide-react";
import api from "@/lib/api";
import { TelemetryStats } from "@/lib/types";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";

export default function TelemetryPage() {
  const qc = useQueryClient();

  const { data: telemetry, isLoading } = useQuery({
    queryKey: ["telemetry"],
    queryFn: () => api.get<TelemetryStats>("/routing/telemetry").then((r) => r.data),
    refetchInterval: 5000,
  });

  const policyMutation = useMutation({
    mutationFn: (policy: string) => api.put("/routing/config", { policy }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["telemetry"] }),
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const modelDist = telemetry?.model_distribution ?? {};
  const recentLogs = telemetry?.recent_logs ?? [];
  const models = telemetry?.available_models ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="font-display text-3xl font-bold text-black">
            Multi-LLM Router Telemetry
          </h1>
          <p className="text-zinc-500 mt-1 text-sm">
            Real-time analytics and adaptive learning policy metrics for LLM allocation.
          </p>
        </div>

        {/* Policy Switcher */}
        <div className="flex items-center gap-2 bg-zinc-100 p-1.5 rounded-xl border border-zinc-200">
          <span className="text-xs text-zinc-500 px-2 font-semibold">Policy:</span>
          <Button
            size="sm"
            variant={telemetry?.active_policy === "heuristic" ? "primary" : "ghost"}
            onClick={() => policyMutation.mutate("heuristic")}
            isLoading={policyMutation.isPending && policyMutation.variables === "heuristic"}
          >
            Heuristic
          </Button>
          <Button
            size="sm"
            variant={telemetry?.active_policy === "bandit" ? "secondary" : "ghost"}
            onClick={() => policyMutation.mutate("bandit")}
            isLoading={policyMutation.isPending && policyMutation.variables === "bandit"}
          >
            Bandit (LinUCB)
          </Button>
        </div>
      </motion.div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { icon: Layers, label: "Total Requests", value: telemetry?.total_requests ?? 0, accent: "bg-primary-100 text-primary-600" },
          { icon: Zap, label: "Avg Latency", value: `${telemetry?.avg_latency_ms ?? 0} ms`, accent: "bg-amber-100 text-amber-600" },
          { icon: DollarSign, label: "Est. Total Cost", value: `$${(telemetry?.total_estimated_cost_usd ?? 0).toFixed(4)}`, accent: "bg-emerald-100 text-emerald-600" },
          { icon: Activity, label: "Avg Reward", value: (telemetry?.avg_reward_score ?? 0).toFixed(2), accent: "bg-rose-100 text-rose-600" },
        ].map(({ icon: Icon, label, value, accent }) => (
          <Card key={label} className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${accent}`}>
              <Icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-400">{label}</p>
              <p className="font-display text-2xl font-bold text-black">{value}</p>
            </div>
          </Card>
        ))}
      </div>

      {/* Model Pool & Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Pool Registry */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-primary-600" /> Multi-LLM Model Pool
            </CardTitle>
          </CardHeader>
          <div className="space-y-3">
            {models.map((m) => (
              <div
                key={m.model_id}
                className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-semibold text-black">{m.display_name}</p>
                  <p className="text-xs text-zinc-400 font-mono">{m.model_id}</p>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-zinc-500">
                    Reasoning: <strong className="text-primary-600">{m.reasoning_score}</strong>
                  </span>
                  <span className="text-zinc-500">
                    Code: <strong className="text-emerald-600">{m.code_score}</strong>
                  </span>
                  <Badge variant="neutral" className="capitalize">{m.tier}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Allocation Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" /> Allocation Distribution
            </CardTitle>
          </CardHeader>
          {Object.keys(modelDist).length === 0 ? (
            <p className="text-sm text-zinc-400 py-6 text-center">
              No routing requests logged yet. Generate roadmaps or quizzes to see allocation telemetry.
            </p>
          ) : (
            <div className="space-y-4">
              {Object.entries(modelDist).map(([model, pct]) => (
                <div key={model} className="space-y-1.5">
                  <div className="flex justify-between text-sm">
                    <span className="text-black font-mono text-xs font-medium">{model}</span>
                    <span className="font-bold text-black">{pct}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-zinc-100 overflow-hidden">
                    <div
                      className="h-full bg-primary-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Recent Routing Decision Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Routing Logs</CardTitle>
        </CardHeader>
        {recentLogs.length === 0 ? (
          <p className="text-sm text-zinc-400 py-4 text-center">No recent log entries.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-zinc-200 text-xs text-zinc-500 uppercase">
                  <th className="py-3 px-4 font-semibold">Timestamp</th>
                  <th className="py-3 px-4 font-semibold">Task Type</th>
                  <th className="py-3 px-4 font-semibold">Model Selected</th>
                  <th className="py-3 px-4 font-semibold">Policy</th>
                  <th className="py-3 px-4 font-semibold">Latency</th>
                  <th className="py-3 px-4 font-semibold">Reward</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {recentLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-zinc-50 transition">
                    <td className="py-3 px-4 text-xs text-zinc-500">
                      {new Date(log.created_at).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 font-mono text-xs text-primary-600 font-semibold">
                      {log.task_type}
                    </td>
                    <td className="py-3 px-4 font-semibold text-black text-sm">{log.selected_model}</td>
                    <td className="py-3 px-4">
                      <Badge variant={log.routing_policy === "bandit" ? "default" : "neutral"}>
                        {log.routing_policy}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-xs text-zinc-500">
                      {log.latency_ms ? `${log.latency_ms} ms` : "—"}
                    </td>
                    <td className="py-3 px-4 font-mono text-xs text-emerald-700 font-semibold">
                      {log.reward_score !== null ? log.reward_score.toFixed(2) : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
