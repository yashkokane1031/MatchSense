"use client";

import React from "react";
import * as Tooltip from "@radix-ui/react-tooltip";

interface ScoreHeatmapProps {
  homeTeam: string;
  awayTeam: string;
  scoreDistribution: number[][]; // 5x5 matrix
}

export function computeCellAlpha(prob: number, maxProb: number): number {
  if (maxProb <= 0) return 0.08;
  const s = Math.sqrt(Math.max(0, prob) / maxProb);
  return 0.08 + 0.82 * Math.min(1, s);
}

export function ScoreHeatmap({ homeTeam, awayTeam, scoreDistribution }: ScoreHeatmapProps) {
  let maxProb = 0;
  for (let i = 0; i < 5; i++) {
    for (let j = 0; j < 5; j++) {
      const p = scoreDistribution[i]?.[j] ?? 0;
      if (p > maxProb) maxProb = p;
    }
  }

  return (
    <Tooltip.Provider delayDuration={150}>
      <div className="w-full">
        <div className="text-xs text-slate-400 mb-2 flex justify-between">
          <span>Home ({homeTeam}) ↓</span>
          <span>Away ({awayTeam}) →</span>
        </div>
        <div
          role="grid"
          aria-label="Poisson Score Distribution Grid"
          className="grid grid-cols-5 gap-1.5 p-2 bg-[#0a0d14]/60 rounded-xl border border-white/5"
        >
          {scoreDistribution.slice(0, 5).map((row, i) =>
            row.slice(0, 5).map((prob, j) => {
              const alpha = computeCellAlpha(prob, maxProb);
              const isMax = prob === maxProb && prob > 0;
              const isDraw = i === j;
              const percentStr = (prob * 100).toFixed(1);
              const oddsStr = prob > 0 ? (1 / prob).toFixed(1) : "—";

              return (
                <Tooltip.Root key={`${i}-${j}`}>
                  <Tooltip.Trigger asChild>
                    <div
                      role="gridcell"
                      tabIndex={0}
                      className={`h-12 rounded-lg flex flex-col items-center justify-center cursor-pointer transition-all hover:scale-105 focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                        isMax ? "ring-2 ring-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.25)]" : ""
                      } ${isDraw ? "border border-dashed border-slate-500/40" : ""}`}
                      style={{ backgroundColor: `rgba(14, 165, 233, ${alpha})` }}
                    >
                      <span className="text-[10px] font-mono text-slate-300/80">
                        {i} - {j}
                      </span>
                      <span className="text-xs font-mono font-semibold text-white tracking-tight">
                        {percentStr}%
                      </span>
                    </div>
                  </Tooltip.Trigger>
                  <Tooltip.Portal>
                    <Tooltip.Content
                      side="top"
                      className="bg-slate-900/95 border border-white/10 text-white text-xs px-3 py-2 rounded-lg shadow-xl z-50 backdrop-blur-md"
                    >
                      <p className="font-semibold text-cyan-400">
                        {homeTeam} {i} – {j} {awayTeam}
                      </p>
                      <p className="text-slate-300 font-mono">
                        Probability: <span className="text-white font-bold">{percentStr}%</span>
                      </p>
                      <p className="text-slate-400 text-[11px] font-mono">
                        Implied Odds: {oddsStr}
                      </p>
                      <Tooltip.Arrow className="fill-slate-900/95" />
                    </Tooltip.Content>
                  </Tooltip.Portal>
                </Tooltip.Root>
              );
            })
          )}
        </div>
      </div>
    </Tooltip.Provider>
  );
}
