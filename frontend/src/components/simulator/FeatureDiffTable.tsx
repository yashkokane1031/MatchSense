import React from "react";

export function FeatureDiffTable({
  features,
}: {
  features?: Record<string, unknown> | null;
}) {
  if (!features || Object.keys(features).length === 0) {
    return (
      <div className="mt-4 p-3 rounded bg-slate-900/40 border border-white/5 text-xs text-slate-400 text-center">
        Feature breakdown unavailable
      </div>
    );
  }

  const formatVal = (val: unknown) => {
    if (val === null || val === undefined || val === "—") return "—";
    if (typeof val === "number") {
      return val > 0 ? `+${val}` : `${val}`;
    }
    return String(val);
  };

  const items = [
    { label: "Elo Differential (Δ Elo)", value: features.elo_diff },
    { label: "Rolling Form (Last 5 Pts)", value: features.form_pts_diff },
    { label: "Shots on Target Diff", value: features.sot_diff },
    { label: "Rest Days Differential", value: features.rest_days_diff },
  ];

  const hasAnyValue = items.some((it) => it.value !== null && it.value !== undefined);
  if (!hasAnyValue) {
    return (
      <div className="mt-4 p-3 rounded bg-slate-900/40 border border-white/5 text-xs text-slate-400 text-center">
        Feature breakdown unavailable for this pairing
      </div>
    );
  }

  return (
    <div className="space-y-2 mt-4">
      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        XGBoost Match Differentials
      </h4>
      <div className="space-y-1.5">
        {items.map((it, idx) => (
          <div
            key={idx}
            className="flex justify-between text-xs py-1 px-2.5 rounded bg-slate-900/40 border border-white/5"
          >
            <span className="text-slate-400">{it.label}</span>
            <span className="font-mono text-white font-medium">{formatVal(it.value)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

