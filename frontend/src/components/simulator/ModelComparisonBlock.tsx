import React from "react";
import { ScoreHeatmap } from "./ScoreHeatmap";
import { FeatureDiffTable } from "./FeatureDiffTable";
import type { ComparePredictionResponse } from "@/types";

interface ModelComparisonBlockProps {
  data: ComparePredictionResponse;
  homeTeam: string;
  awayTeam: string;
}

export function ModelComparisonBlock({
  data,
  homeTeam,
  awayTeam,
}: ModelComparisonBlockProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Dixon-Coles Card */}
      <div className="p-6 rounded-2xl bg-[#111622]/80 border border-cyan-500/20 shadow-[0_0_25px_rgba(14,165,233,0.05)]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white">Dixon-Coles</h3>
            <span className="text-xs text-cyan-400 font-mono">
              Generative · Bivariate Poisson
            </span>
          </div>
          {data.dixon_coles.predicted_score && (
            <span className="px-3 py-1 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 font-mono text-sm font-semibold">
              Most Likely: {data.dixon_coles.predicted_score.home} –{" "}
              {data.dixon_coles.predicted_score.away}
            </span>
          )}
        </div>

        <div className="grid grid-cols-3 gap-2 text-center py-3 px-4 rounded-xl bg-slate-900/50 mb-6 font-mono">
          <div>
            <p className="text-xs text-slate-400">Home</p>
            <p className="text-base font-bold text-emerald-400">
              {(data.dixon_coles.prob_home * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Draw</p>
            <p className="text-base font-bold text-slate-300">
              {(data.dixon_coles.prob_draw * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Away</p>
            <p className="text-base font-bold text-amber-400">
              {(data.dixon_coles.prob_away * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {data.dixon_coles.score_distribution && (
          <ScoreHeatmap
            homeTeam={homeTeam}
            awayTeam={awayTeam}
            scoreDistribution={data.dixon_coles.score_distribution}
          />
        )}
      </div>

      {/* XGBoost Card */}
      <div className="p-6 rounded-2xl bg-[#111622]/80 border border-violet-500/20 shadow-[0_0_25px_rgba(139,92,246,0.05)]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white">XGBoost</h3>
            <span className="text-xs text-violet-400 font-mono">
              Discriminative · Gradient Boosted Trees
            </span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 text-center py-3 px-4 rounded-xl bg-slate-900/50 mb-6 font-mono">
          <div>
            <p className="text-xs text-slate-400">Home</p>
            <p className="text-base font-bold text-emerald-400">
              {(data.xgboost.prob_home * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Draw</p>
            <p className="text-base font-bold text-slate-300">
              {(data.xgboost.prob_draw * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-400">Away</p>
            <p className="text-base font-bold text-amber-400">
              {(data.xgboost.prob_away * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {data.xgboost.features && (
          <FeatureDiffTable
            features={data.xgboost.features as Record<string, unknown>}
          />
        )}
      </div>
    </div>
  );
}
