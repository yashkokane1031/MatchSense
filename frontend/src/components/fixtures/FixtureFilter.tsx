"use client";

import { PREMIER_LEAGUE_TEAMS } from "@/lib/constants";

interface FixtureFilterProps {
  selectedTeam: string;
  onSelectTeam: (team: string) => void;
  searchTerm: string;
  onSearchChange: (search: string) => void;
}

export function FixtureFilter({
  selectedTeam,
  onSelectTeam,
  searchTerm,
  onSearchChange,
}: FixtureFilterProps) {
  const teamList = Object.keys(PREMIER_LEAGUE_TEAMS).sort();

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-6">
      <div className="relative flex-1 max-w-sm">
        <input
          type="text"
          placeholder="Filter by club..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full bg-[#111622] border border-white/10 rounded-xl px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
        />
        {searchTerm && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-3 top-2.5 text-xs text-slate-400 hover:text-white"
          >
            ✕
          </button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <select
          value={selectedTeam}
          onChange={(e) => onSelectTeam(e.target.value)}
          className="bg-[#111622] border border-white/10 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 cursor-pointer"
        >
          <option value="ALL">All 20 Premier League Clubs</option>
          {teamList.map((team) => (
            <option key={team} value={team}>
              {team}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
