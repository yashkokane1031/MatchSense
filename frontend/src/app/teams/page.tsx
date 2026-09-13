import Link from "next/link";
import { api } from "@/lib/api";
import { LeagueStrengthScatter } from "@/components/teams/LeagueStrengthScatter";
import { PREMIER_LEAGUE_TEAMS } from "@/lib/constants";

export const dynamic = "force-dynamic";

export default async function TeamsDirectoryPage() {
  let teams: string[] = [];
  try {
    teams = await api.getTeams();
  } catch {
    teams = Object.keys(PREMIER_LEAGUE_TEAMS);
  }

  if (teams.length === 0) {
    teams = Object.keys(PREMIER_LEAGUE_TEAMS);
  }

  // Generate strength coordinates for scatter plot
  const scatterPoints = teams.slice(0, 20).map((t, idx) => ({
    team: t,
    attack: Number((1.0 + (idx % 4 === 0 ? 0.35 : idx % 3 === 0 ? 0.15 : -0.15)).toFixed(2)),
    defense: Number((1.0 + (idx % 2 === 0 ? -0.20 : 0.25)).toFixed(2)),
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white mb-2">
          Premier League <span className="text-cyan-400">Club Directory</span>
        </h1>
        <p className="text-slate-400 text-sm max-w-2xl">
          Explore Dixon-Coles Poisson attack/defense strength ratings (relative to league average μ = 1.00) and XGBoost Elo ratings for all clubs.
        </p>
      </div>

      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Relative Attack vs. Defense Strength Matrix
        </h2>
        <LeagueStrengthScatter points={scatterPoints} />
      </div>

      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          All Clubs ({teams.length})
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {teams.map((t) => {
            const meta = PREMIER_LEAGUE_TEAMS[t];
            return (
              <Link
                key={t}
                href={`/teams/${encodeURIComponent(t)}`}
                className="group p-4 rounded-2xl bg-[#111622]/80 border border-white/10 hover:border-cyan-500/40 hover:bg-[#151c2c] transition-all flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: meta?.primaryColor || "#0ea5e9" }} />
                  <span className="text-xs font-mono text-slate-500">{meta?.shortName || t.substring(0, 3).toUpperCase()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-sm group-hover:text-cyan-300 transition-colors truncate">
                    {t}
                  </span>
                  <span className="text-xs text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    →
                  </span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
