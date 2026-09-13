"use client";

import { useHealthStatus } from "@/hooks/useHealthStatus";

export function HealthBadge() {
  const { health, refetch } = useHealthStatus();

  const config = {
    healthy: {
      dot: "bg-emerald-400 animate-pulse",
      text: "Models Live",
      border: "border-emerald-500/30 text-emerald-300 bg-emerald-950/20",
    },
    degraded: {
      dot: "bg-amber-400",
      text: "System Degraded",
      border: "border-amber-500/30 text-amber-300 bg-amber-950/20",
    },
    offline: {
      dot: "bg-rose-500",
      text: "API Offline",
      border: "border-rose-500/30 text-rose-300 bg-rose-950/20",
    },
  }[health.derivedStatus];

  return (
    <button
      onClick={() => refetch()}
      title={health.message || "Click to check API status"}
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${config.border}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      <span>{config.text}</span>
    </button>
  );
}
