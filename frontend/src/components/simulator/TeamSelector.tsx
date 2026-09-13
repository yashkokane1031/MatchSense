"use client";

import { PREMIER_LEAGUE_TEAMS } from "@/lib/constants";

interface TeamSelectorProps {
  homeTeam: string;
  awayTeam: string;
  onSelectHome: (team: string) => void;
  onSelectAway: (team: string) => void;
  onSwap: () => void;
}

export function TeamSelector({
  homeTeam,
  awayTeam,
  onSelectHome,
  onSelectAway,
  onSwap,
}: TeamSelectorProps) {
  const teams = Object.keys(PREMIER_LEAGUE_TEAMS).sort();

  return (
    <div className="flex flex-col sm:flex-row items-center gap-4 mb-8 bg-[#111622]/90 p-5 rounded-2xl border border-white/10">
      <div className="w-full sm:w-1/2">
        <label className="block text-xs font-semibold text-slate-400 mb-1.5">
          Home Club
        </label>
        <select
          value={homeTeam}
          onChange={(e) => onSelectHome(e.target.value)}
          className="w-full bg-[#0a0d14] text-white border border-white/15 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 cursor-pointer"
        >
          {teams.map((t) => (
            <option key={t} value={t} disabled={t === awayTeam}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={onSwap}
        className="p-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-slate-300 transition-colors mt-2 sm:mt-5 focus:outline-none focus:ring-2 focus:ring-cyan-400"
        title="Swap home and away"
        aria-label="Swap home and away"
      >
        <span className="text-base font-bold">⇄</span>
      </button>

      <div className="w-full sm:w-1/2">
        <label className="block text-xs font-semibold text-slate-400 mb-1.5">
          Away Club
        </label>
        <select
          value={awayTeam}
          onChange={(e) => onSelectAway(e.target.value)}
          className="w-full bg-[#0a0d14] text-white border border-white/15 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 cursor-pointer"
        >
          {teams.map((t) => (
            <option key={t} value={t} disabled={t === homeTeam}>
              {t}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
