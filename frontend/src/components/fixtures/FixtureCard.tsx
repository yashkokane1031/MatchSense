import Link from "next/link";
import { ModelProbabilityBar } from "@/components/common/ModelProbabilityBar";
import type { FixtureCard as FixtureCardType } from "@/types";

export function FixtureCard({ fixture }: { fixture: FixtureCardType }) {
  const dc = fixture.predictions?.dixon_coles as
    | { prob_home: number; prob_draw: number; prob_away: number }
    | undefined;
  const xgb = fixture.predictions?.xgboost as
    | { prob_home: number; prob_draw: number; prob_away: number }
    | undefined;

  const kickoff = new Date(fixture.kickoff_time).toLocaleString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="p-5 rounded-2xl bg-[#111622]/80 border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between text-xs text-slate-400 mb-4 pb-2 border-b border-white/5">
          <span>GW {fixture.gameweek}</span>
          <span>{kickoff}</span>
        </div>

        <div className="flex items-center justify-between font-semibold text-base text-white mb-6">
          <span className="truncate">{fixture.home_team}</span>
          <span className="text-slate-500 font-mono text-sm px-2">vs</span>
          <span className="truncate text-right">{fixture.away_team}</span>
        </div>

        <div className="space-y-3">
          {dc ? (
            <ModelProbabilityBar
              modelName="Dixon-Coles"
              probHome={dc.prob_home}
              probDraw={dc.prob_draw}
              probAway={dc.prob_away}
            />
          ) : (
            <div className="text-xs text-slate-500 bg-slate-900/40 p-2 rounded">
              Dixon-Coles updating...
            </div>
          )}

          {xgb ? (
            <ModelProbabilityBar
              modelName="XGBoost"
              probHome={xgb.prob_home}
              probDraw={xgb.prob_draw}
              probAway={xgb.prob_away}
            />
          ) : (
            <div className="text-xs text-slate-500 bg-slate-900/40 p-2 rounded">
              XGBoost updating...
            </div>
          )}
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-white/5 flex justify-end">
        <Link
          href={`/simulator?home=${encodeURIComponent(fixture.home_team)}&away=${encodeURIComponent(fixture.away_team)}`}
          className="text-xs font-medium text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1"
        >
          Simulate in H2H →
        </Link>
      </div>
    </div>
  );
}
