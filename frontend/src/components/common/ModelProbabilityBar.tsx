"use client";

interface ModelProbabilityBarProps {
  modelName: "Dixon-Coles" | "XGBoost";
  probHome: number;
  probDraw: number;
  probAway: number;
}

export function ModelProbabilityBar({
  modelName,
  probHome,
  probDraw,
  probAway,
}: ModelProbabilityBarProps) {
  const isDixon = modelName === "Dixon-Coles";
  const badgeColor = isDixon
    ? "text-cyan-400 border-cyan-500/30 bg-cyan-950/20"
    : "text-violet-400 border-violet-500/30 bg-violet-950/20";
  const dotColor = isDixon ? "bg-cyan-400" : "bg-violet-400";

  const pHome = Math.max(0, probHome);
  const pDraw = Math.max(0, probDraw);
  const pAway = Math.max(0, probAway);

  const homePct = (pHome * 100).toFixed(1);
  const drawPct = (pDraw * 100).toFixed(1);
  const awayPct = (pAway * 100).toFixed(1);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[11px] font-medium ${badgeColor}`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
          {modelName}
        </span>
        <span className="font-mono text-slate-400 text-[11px]">
          H: <span className="text-emerald-400 font-semibold">{homePct}%</span> · D:{" "}
          <span className="text-slate-300">{drawPct}%</span> · A:{" "}
          <span className="text-amber-400 font-semibold">{awayPct}%</span>
        </span>
      </div>

      <div className="w-full h-3 rounded-full overflow-hidden flex bg-slate-900 border border-white/5">
        <div
          style={{ width: `${homePct}%` }}
          className="bg-emerald-500 h-full transition-all duration-400 ease-out"
          title={`Home Win: ${homePct}%`}
        />
        <div
          style={{ width: `${drawPct}%` }}
          className="bg-slate-500 h-full transition-all duration-400 ease-out"
          title={`Draw: ${drawPct}%`}
        />
        <div
          style={{ width: `${awayPct}%` }}
          className="bg-amber-500 h-full transition-all duration-400 ease-out"
          title={`Away Win: ${awayPct}%`}
        />
      </div>
    </div>
  );
}
