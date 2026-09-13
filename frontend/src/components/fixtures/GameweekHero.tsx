import React from "react";
import type { FixtureCard } from "@/types";

interface GameweekHeroProps {
  fixtures: FixtureCard[];
}

export function GameweekHero({ fixtures }: GameweekHeroProps) {
  const currentGw = fixtures.length > 0 ? fixtures[0].gameweek : 28;

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#111622] via-[#0e1420] to-[#0a0d14] border border-white/10 p-6 sm:p-8 mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 mb-3">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            Gameweek {currentGw} Matchweek Hub
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Premier League <span className="text-cyan-400">Match Forecasts</span>
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1 max-w-xl">
            Independent side-by-side probabilistic outcomes from generative bivariate Poisson
            (Dixon-Coles) and discriminative gradient-boosted trees (XGBoost).
          </p>
        </div>

        <div className="flex items-center gap-3 self-start sm:self-center">
          <div className="px-4 py-2 rounded-xl bg-slate-900/80 border border-white/5 text-center">
            <span className="text-[10px] uppercase font-mono text-slate-400 block">Fixtures</span>
            <span className="text-lg font-bold text-white font-mono">{fixtures.length}</span>
          </div>
          <div className="px-4 py-2 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-center">
            <span className="text-[10px] uppercase font-mono text-cyan-300 block">Dixon-Coles</span>
            <span className="text-xs font-semibold text-cyan-400">Generative</span>
          </div>
          <div className="px-4 py-2 rounded-xl bg-violet-950/20 border border-violet-500/20 text-center">
            <span className="text-[10px] uppercase font-mono text-violet-300 block">XGBoost</span>
            <span className="text-xs font-semibold text-violet-400">Discriminative</span>
          </div>
        </div>
      </div>
    </div>
  );
}
