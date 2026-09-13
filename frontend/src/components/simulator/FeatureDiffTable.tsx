import React from "react";

export function FeatureDiffTable({
  features,
}: {
  features: Record<string, unknown>;
}) {
  if (!features || Object.keys(features).length === 0) {
    return <div className="text-xs text-slate-500">Feature values unavailable</div>;
  }

  const items = [
    { label: "Elo Differential (Δ Elo)", value: features.elo_diff ?? "—" },
    { label: "Rolling Form (Last 5 Pts)", value: features.form_pts_diff ?? "—" },
    { label: "Shots on Target Diff", value: features.sot_diff ?? "—" },
    { label: "Rest Days Differential", value: features.rest_days_diff ?? "—" },
  ];

  return (
    <div className="space-y-2 mt-4">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        XGBoost Input Features
      </h4>
      <div className="space-y-1.5">
        {items.map((it, idx) => (
          <div
            key={idx}
            className="flex justify-between text-xs py-1 px-2.5 rounded bg-slate-900/40 border border-white/5"
          >
            <span className="text-slate-400">{it.label}</span>
            <span className="font-mono text-white font-medium">{String(it.value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
